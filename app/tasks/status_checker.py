"""
Status checker tasks for monitoring application statuses
"""
from datetime import datetime, timedelta
from app.celery_config import celery
from app import db
from app.models.application import Application
from app.models.automation_log import AutomationLog


@celery.task(name='app.tasks.status_checker.check_all_application_statuses')
def check_all_application_statuses():
    """
    Check status of all recent applications
    Runs daily at 10 AM via Celery Beat
    """
    # Get applications from last 30 days that aren't rejected or have old status
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    applications = Application.query.filter(
        Application.applied_at >= cutoff_date,
        Application.status.in_(['sent', 'viewed'])
    ).all()

    checked = 0
    updated = 0

    for app in applications:
        try:
            check_application_status.delay(app.id)
            checked += 1
        except Exception as e:
            print(f"Error queuing status check for application {app.id}: {str(e)}")

    return f"Queued status checks for {checked} applications"


@celery.task(name='app.tasks.status_checker.check_application_status')
def check_application_status(application_id):
    """
    Check status of a specific application
    TODO: Implement platform-specific status checking
    """
    try:
        application = Application.query.get(application_id)
        if not application:
            return f"Application {application_id} not found"

        # Check status on platform
        new_status = check_status_on_platform(
            platform=application.platform,
            job_url=application.job_url
        )

        if new_status and new_status != application.status:
            old_status = application.status
            application.status = new_status
            application.last_status_update = datetime.utcnow()

            # Log status change
            log = AutomationLog(
                user_id=application.user_id,
                action_type='status_update',
                status='success',
                message=f"Application status changed from {old_status} to {new_status}",
                metadata={
                    'application_id': application.id,
                    'company': application.company_name,
                    'job_title': application.job_title
                }
            )
            db.session.add(log)
            db.session.commit()

            # TODO: Send notification to user about status change
            # from app.tasks.notifications import send_status_update_email
            # send_status_update_email.delay(application.user_id, application.id)

            return f"Status updated to {new_status}"
        else:
            return f"No status change detected"

    except Exception as e:
        db.session.rollback()
        return f"Error checking status: {str(e)}"


def check_status_on_platform(platform, job_url):
    """
    Check application status on specific platform
    TODO: Implement platform-specific status checking

    Returns: new_status string or None if unchanged
    """
    # Example implementation:
    # if platform.lower() == 'linkedin':
    #     bot = LinkedInBot()
    #     return bot.check_application_status(job_url)

    # For now, return None (no change)
    return None
