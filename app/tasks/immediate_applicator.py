"""
Immediate job application task - starts applying as soon as config is saved
"""
from datetime import datetime
from app.celery_config import celery
from app import db
from app.models.user import User
from app.models.job_search_config import JobSearchConfig
from app.models.resume import Resume
from app.models.application import Application
from app.models.subscription import Subscription
from app.models.automation_log import AutomationLog
from app.models.platform_credential import PlatformCredential


@celery.task(name='app.tasks.immediate_applicator.start_immediate_applications')
def start_immediate_applications(user_id, config_id):
    """
    Start applying to jobs IMMEDIATELY when config is saved
    Applies to ALL matching jobs on configured platforms
    Processes both primary and secondary configs simultaneously
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        config = JobSearchConfig.query.get(config_id)
        if not config:
            return {"success": False, "error": "Config not found"}

        # Check subscription limits
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        if subscription and subscription.applications_used >= subscription.applications_limit:
            log_event(user_id, 'immediate_apply', 'failed', 'Application limit reached')
            return {"success": False, "error": "Application limit reached"}

        # Get platform credentials
        platforms = config.platforms or []
        if not platforms:
            return {"success": False, "error": "No platforms configured"}

        # Get user's resumes
        resumes = Resume.query.filter_by(user_id=user_id).all()
        if not resumes:
            return {"success": False, "error": "No resumes uploaded"}

        total_applied = 0
        errors = []

        # Apply to both PRIMARY and SECONDARY configs simultaneously
        configs_to_process = []

        # Add primary config
        if config.primary_job_title:
            configs_to_process.append({
                'type': 'primary',
                'job_title': config.primary_job_title,
                'location': config.primary_location,
                'job_type': config.primary_job_type,
                'min_salary': config.primary_min_salary,
                'max_salary': config.primary_max_salary,
                'experience_level': config.primary_experience_level,
                'remote_preference': config.primary_remote_preference,
                'keywords': config.primary_keywords or [],
                'resume_id': config.primary_resume_id
            })

        # Add secondary config
        if config.secondary_job_title:
            configs_to_process.append({
                'type': 'secondary',
                'job_title': config.secondary_job_title,
                'location': config.secondary_location,
                'job_type': config.secondary_job_type,
                'min_salary': config.secondary_min_salary,
                'max_salary': config.secondary_max_salary,
                'experience_level': config.secondary_experience_level,
                'remote_preference': config.secondary_remote_preference,
                'keywords': config.secondary_keywords or [],
                'resume_id': config.secondary_resume_id
            })

        # Process each config
        for search_config in configs_to_process:
            # Get appropriate resume
            resume = get_matching_resume(resumes, search_config)
            if not resume:
                errors.append(f"No matching resume for {search_config['type']} config")
                continue

            # Process each platform
            for platform in platforms:
                try:
                    # Get platform credentials
                    credential = PlatformCredential.query.filter_by(
                        user_id=user_id,
                        platform=platform.lower()
                    ).first()

                    if not credential:
                        errors.append(f"No credentials for {platform}")
                        continue

                    # Search and apply to jobs on this platform
                    applied_count = search_and_apply_immediate(
                        user=user,
                        config=config,
                        search_config=search_config,
                        platform=platform,
                        credential=credential,
                        resume=resume,
                        subscription=subscription
                    )

                    total_applied += applied_count

                except Exception as e:
                    errors.append(f"Error on {platform}: {str(e)}")

        # Log completion
        log_event(
            user_id,
            'immediate_apply',
            'success',
            f"Applied to {total_applied} jobs",
            details={'errors': errors if errors else None}
        )

        return {
            "success": True,
            "total_applied": total_applied,
            "errors": errors
        }

    except Exception as e:
        log_event(user_id, 'immediate_apply', 'failed', f"Error: {str(e)}")
        return {"success": False, "error": str(e)}


def get_matching_resume(resumes, search_config):
    """
    Get resume that matches the job search config
    Matches based on resume filename or job_type_tag
    """
    job_title = search_config['job_title'].lower()
    resume_id = search_config.get('resume_id')

    # First, try to use specified resume
    if resume_id:
        for resume in resumes:
            if resume.id == resume_id:
                return resume

    # Match by filename or job_type_tag
    for resume in resumes:
        filename = (resume.filename or '').lower()
        job_tag = (resume.job_type_tag or '').lower()

        # Check if job title keywords are in resume name/tag
        job_keywords = job_title.split()
        for keyword in job_keywords:
            if len(keyword) > 3:  # Only meaningful keywords
                if keyword in filename or keyword in job_tag:
                    return resume

    # Fall back to default resume
    for resume in resumes:
        if resume.is_default:
            return resume

    # Return first resume if no match
    return resumes[0] if resumes else None


def search_and_apply_immediate(user, config, search_config, platform, credential, resume, subscription):
    """
    Search for jobs and apply IMMEDIATELY (no queue)
    Applies to ALL matching jobs found
    """
    from app.automation.linkedin_bot import LinkedInBot
    from app.automation.indeed_bot import IndeedBot

    applied_count = 0

    try:
        # Prepare user profile with credentials
        user_profile = user.to_dict()

        if platform.lower() == 'linkedin':
            user_profile['linkedin_email'] = credential.get_username()
            user_profile['linkedin_password'] = credential.get_password()
            bot = LinkedInBot(user_profile=user_profile, resume_base64=resume.file_base64)
        elif platform.lower() == 'indeed':
            user_profile['indeed_email'] = credential.get_username()
            user_profile['indeed_password'] = credential.get_password()
            bot = IndeedBot(user_profile=user_profile, resume_base64=resume.file_base64)
        else:
            return 0

        # Login to platform
        if not bot.login():
            log_event(user.id, 'platform_login', 'failed', f"Failed to login to {platform}")
            return 0

        # Search for jobs
        jobs = bot.search_jobs(
            job_title=search_config['job_title'],
            location=search_config['location'],
            job_type=search_config['job_type'],
            experience_level=search_config['experience_level'],
            remote_preference=search_config['remote_preference'],
            keywords=search_config['keywords']
        )

        # Apply to ALL matching jobs
        for job in jobs:
            try:
                # Check if already applied
                existing = Application.query.filter_by(
                    user_id=user.id,
                    job_url=job['job_url']
                ).first()

                if existing:
                    continue  # Skip already applied

                # Check subscription limit
                if subscription and subscription.applications_used >= subscription.applications_limit:
                    break  # Stop if limit reached

                # Apply to job
                success, message = bot.apply_to_job(job['job_url'])

                if success:
                    # Create application record
                    application = Application(
                        user_id=user.id,
                        company_name=job['company_name'],
                        job_title=job['job_title'],
                        job_type=job.get('job_type'),
                        location=job.get('location'),
                        salary_range=job.get('salary_range'),
                        platform=platform,
                        job_url=job['job_url'],
                        status='sent',
                        resume_used_id=resume.id,
                        applied_at=datetime.utcnow()
                    )
                    db.session.add(application)

                    # Update subscription usage
                    if subscription:
                        subscription.applications_used += 1

                    # Update resume last used
                    resume.last_used_at = datetime.utcnow()

                    applied_count += 1
                    db.session.commit()

                    # Log success
                    log_event(
                        user.id,
                        'job_apply',
                        'success',
                        f"Applied to {job['company_name']} - {job['job_title']}",
                        details={'platform': platform, 'config_type': search_config['type']}
                    )

            except Exception as e:
                print(f"Error applying to job: {str(e)}")
                continue

        # Logout
        bot.logout()

        return applied_count

    except Exception as e:
        print(f"Error in search_and_apply_immediate: {str(e)}")
        return applied_count


def log_event(user_id, action_type, status, message, details=None):
    """Log automation event"""
    try:
        log = AutomationLog(
            user_id=user_id,
            action_type=action_type,
            status=status,
            message=message,
            details=details or {}
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging event: {str(e)}")
