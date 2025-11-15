"""
Notification tasks for sending emails and alerts
"""
from datetime import datetime, timedelta
from app.celery_config import celery
from app import db
from app.models.user import User
from app.models.application import Application
from app.models.job_queue import JobQueue


@celery.task(name='app.tasks.notifications.send_all_daily_summaries')
def send_all_daily_summaries():
    """
    Send daily summaries to all users
    Runs daily at 8 AM via Celery Beat
    """
    users = User.query.all()

    sent = 0
    for user in users:
        try:
            send_daily_summary.delay(user.id)
            sent += 1
        except Exception as e:
            print(f"Error queuing daily summary for user {user.id}: {str(e)}")

    return f"Queued daily summaries for {sent} users"


@celery.task(name='app.tasks.notifications.send_daily_summary')
def send_daily_summary(user_id):
    """
    Send daily summary email to user
    TODO: Implement email sending
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"

        # Get yesterday's data
        yesterday = datetime.utcnow() - timedelta(days=1)
        start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0)
        end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59)

        # Applications submitted yesterday
        apps_yesterday = Application.query.filter(
            Application.user_id == user_id,
            Application.applied_at >= start_of_yesterday,
            Application.applied_at <= end_of_yesterday
        ).all()

        # Pending jobs in queue
        pending_jobs = JobQueue.query.filter_by(
            user_id=user_id,
            status='pending'
        ).count()

        # Status updates
        status_updates = Application.query.filter(
            Application.user_id == user_id,
            Application.last_status_update >= start_of_yesterday,
            Application.last_status_update <= end_of_yesterday
        ).filter(
            Application.last_status_update != Application.applied_at
        ).all()

        # Prepare email content
        summary = {
            'applications_submitted': len(apps_yesterday),
            'pending_applications': pending_jobs,
            'status_updates': len(status_updates),
            'applications': [app.to_dict() for app in apps_yesterday[:5]],  # Top 5
            'updates': [app.to_dict() for app in status_updates[:5]]
        }

        # TODO: Send actual email
        # send_email(
        #     to=user.email,
        #     subject=f"DevApply Daily Summary - {apps_yesterday} Applications",
        #     template='daily_summary',
        #     context=summary
        # )

        print(f"[EMAIL] Daily summary for {user.email}:")
        print(f"  - {len(apps_yesterday)} applications submitted")
        print(f"  - {pending_jobs} pending in queue")
        print(f"  - {len(status_updates)} status updates")

        return f"Sent daily summary to {user.email}"

    except Exception as e:
        return f"Error sending daily summary: {str(e)}"


@celery.task(name='app.tasks.notifications.send_status_update_email')
def send_status_update_email(user_id, application_id):
    """
    Send email notification when application status changes
    """
    try:
        user = User.query.get(user_id)
        application = Application.query.get(application_id)

        if not user or not application:
            return "User or application not found"

        # TODO: Send actual email
        print(f"[EMAIL] Status update for {user.email}:")
        print(f"  Application to {application.company_name} - {application.job_title}")
        print(f"  New status: {application.status}")

        return f"Sent status update email to {user.email}"

    except Exception as e:
        return f"Error sending status update: {str(e)}"
