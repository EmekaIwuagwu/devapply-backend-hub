"""
Job applicator tasks for automated job applications
"""
from datetime import datetime, timedelta
import time
from app.celery_config import celery
from app import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_queue import JobQueue
from app.models.application import Application
from app.models.subscription import Subscription
from app.models.automation_log import AutomationLog
from app.utils.rate_limiter import ApplicationRateLimiter


@celery.task(name='app.tasks.job_applicator.process_job_queue')
def process_job_queue():
    """
    Process pending jobs in the queue
    Runs every 30 minutes via Celery Beat
    """
    # Get all pending jobs ordered by priority and scheduled time
    pending_jobs = JobQueue.query.filter_by(
        status='pending'
    ).filter(
        JobQueue.scheduled_for <= datetime.utcnow()
    ).order_by(
        JobQueue.priority.desc(),
        JobQueue.created_at.asc()
    ).limit(50).all()  # Process max 50 jobs per run

    processed = 0
    for job in pending_jobs:
        try:
            # Apply to job
            apply_to_job.delay(job.id)
            processed += 1
        except Exception as e:
            print(f"Error queuing application for job {job.id}: {str(e)}")

    return f"Queued {processed} jobs for application"


@celery.task(name='app.tasks.job_applicator.apply_to_job', bind=True, max_retries=3)
def apply_to_job(self, job_queue_id):
    """
    Apply to a single job using automation
    """
    try:
        queue_item = JobQueue.query.get(job_queue_id)
        if not queue_item:
            return f"Job queue item {job_queue_id} not found"

        # Check if already processing or completed
        if queue_item.status in ['processing', 'applied', 'skipped']:
            return f"Job {job_queue_id} already {queue_item.status}"

        # Update status to processing
        queue_item.status = 'processing'
        queue_item.attempted_at = datetime.utcnow()
        db.session.commit()

        user = User.query.get(queue_item.user_id)
        if not user:
            queue_item.status = 'failed'
            queue_item.error_message = "User not found"
            db.session.commit()
            return "User not found"

        # Check subscription limits
        subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()

        if subscription:
            if subscription.applications_used >= subscription.applications_limit:
                queue_item.status = 'skipped'
                queue_item.error_message = "Application limit reached for subscription"
                db.session.commit()
                return "Application limit reached"

        # Check rate limits
        can_apply, reason, wait_time = ApplicationRateLimiter.can_apply(
            user.id,
            queue_item.platform
        )

        if not can_apply:
            # Reschedule for later
            queue_item.status = 'pending'
            queue_item.scheduled_for = datetime.utcnow() + timedelta(seconds=wait_time)
            db.session.commit()
            return f"Rate limited: {reason}. Rescheduled for later."

        # Get user's resume
        resume = get_user_resume(user.id, queue_item.job_search_config_id)
        if not resume:
            queue_item.status = 'failed'
            queue_item.error_message = "No resume available"
            db.session.commit()
            return "No resume available"

        # Apply to the job
        success, message = apply_to_platform(
            platform=queue_item.platform,
            job_url=queue_item.job_url,
            user=user,
            resume=resume
        )

        if success:
            # Create application record
            application = Application(
                user_id=user.id,
                company_name=queue_item.company_name,
                job_title=queue_item.job_title,
                platform=queue_item.platform,
                job_url=queue_item.job_url,
                status='sent',
                resume_used_id=resume.id,
                applied_at=datetime.utcnow()
            )
            db.session.add(application)

            # Update queue item
            queue_item.status = 'applied'
            queue_item.completed_at = datetime.utcnow()

            # Update subscription usage
            if subscription:
                subscription.applications_used += 1

            # Update resume last_used_at
            resume.last_used_at = datetime.utcnow()

            # Log success
            log = AutomationLog(
                user_id=user.id,
                job_queue_id=queue_item.id,
                action_type='job_apply',
                status='success',
                message=f"Successfully applied to {queue_item.company_name} - {queue_item.job_title}",
                metadata={'platform': queue_item.platform}
            )
            db.session.add(log)

            db.session.commit()

            return f"Successfully applied to {queue_item.company_name}"

        else:
            # Application failed
            queue_item.retry_count += 1

            if queue_item.retry_count >= queue_item.max_retries:
                queue_item.status = 'failed'
                queue_item.error_message = message
            else:
                # Retry later
                queue_item.status = 'pending'
                queue_item.scheduled_for = datetime.utcnow() + timedelta(hours=1)

            # Log failure
            log = AutomationLog(
                user_id=user.id,
                job_queue_id=queue_item.id,
                action_type='job_apply',
                status='failed',
                message=f"Failed to apply: {message}",
                metadata={'platform': queue_item.platform, 'retry_count': queue_item.retry_count}
            )
            db.session.add(log)

            db.session.commit()

            # Retry task if haven't exceeded max retries
            if queue_item.retry_count < queue_item.max_retries:
                raise self.retry(exc=Exception(message), countdown=3600)  # Retry in 1 hour

            return f"Application failed: {message}"

    except Exception as e:
        db.session.rollback()

        # Try to update queue item status
        try:
            queue_item = JobQueue.query.get(job_queue_id)
            if queue_item:
                queue_item.status = 'failed'
                queue_item.error_message = str(e)
                db.session.commit()
        except:
            pass

        return f"Error: {str(e)}"


def get_user_resume(user_id, job_search_config_id=None):
    """Get appropriate resume for job application"""
    # First try to get resume from job search config
    if job_search_config_id:
        from app.models.job_search_config import JobSearchConfig
        config = JobSearchConfig.query.get(job_search_config_id)
        if config and config.primary_resume_id:
            resume = Resume.query.get(config.primary_resume_id)
            if resume:
                return resume

    # Fall back to default resume
    resume = Resume.query.filter_by(
        user_id=user_id,
        is_default=True
    ).first()

    if resume:
        return resume

    # If no default, get most recently uploaded
    resume = Resume.query.filter_by(
        user_id=user_id
    ).order_by(Resume.uploaded_at.desc()).first()

    return resume


def apply_to_platform(platform, job_url, user, resume):
    """
    Apply to job on specific platform
    TODO: Implement platform-specific automation

    Returns: (success: bool, message: str)
    """
    # Import platform-specific bots
    # from app.automation.linkedin_bot import LinkedInBot
    # from app.automation.indeed_bot import IndeedBot

    # Example implementation:
    # if platform.lower() == 'linkedin':
    #     bot = LinkedInBot(user_profile=user.to_dict(), resume_base64=resume.file_base64)
    #     return bot.apply_to_job(job_url)
    # elif platform.lower() == 'indeed':
    #     bot = IndeedBot(user_profile=user.to_dict(), resume_base64=resume.file_base64)
    #     return bot.apply_to_job(job_url)

    # For now, simulate application
    print(f"[SIMULATION] Applying to {platform} job at {job_url}")
    print(f"User: {user.email}, Resume: {resume.filename}")

    # In production, this would:
    # 1. Initialize headless browser (Selenium/Playwright)
    # 2. Navigate to job URL
    # 3. Fill application form
    # 4. Upload resume (convert from base64)
    # 5. Submit application
    # 6. Handle confirmation

    # Simulate success for now
    return True, "Application submitted successfully (simulated)"
