"""
Cleanup tasks for maintaining database hygiene
"""
from datetime import datetime, timedelta
from app.celery_config import celery
from app import db
from app.models.job_listing import JobListing
from app.models.job_queue import JobQueue
from app.models.automation_log import AutomationLog


@celery.task(name='app.tasks.cleanup.clean_old_jobs')
def clean_old_jobs():
    """
    Clean up old job listings and failed queue items
    Runs daily at 2 AM via Celery Beat
    """
    deleted_listings = 0
    deleted_queue = 0
    deleted_logs = 0

    try:
        # Delete job listings older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        old_listings = JobListing.query.filter(
            JobListing.scraped_at < thirty_days_ago
        ).all()

        for listing in old_listings:
            db.session.delete(listing)
            deleted_listings += 1

        # Delete failed/skipped queue items older than 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        old_queue_items = JobQueue.query.filter(
            JobQueue.status.in_(['failed', 'skipped']),
            JobQueue.created_at < seven_days_ago
        ).all()

        for item in old_queue_items:
            db.session.delete(item)
            deleted_queue += 1

        # Delete automation logs older than 90 days
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        old_logs = AutomationLog.query.filter(
            AutomationLog.created_at < ninety_days_ago
        ).all()

        for log in old_logs:
            db.session.delete(log)
            deleted_logs += 1

        db.session.commit()

        return f"Cleaned up {deleted_listings} listings, {deleted_queue} queue items, {deleted_logs} logs"

    except Exception as e:
        db.session.rollback()
        return f"Error during cleanup: {str(e)}"


@celery.task(name='app.tasks.cleanup.deactivate_old_listings')
def deactivate_old_listings():
    """Mark old job listings as inactive instead of deleting"""
    try:
        fourteen_days_ago = datetime.utcnow() - timedelta(days=14)

        updated = JobListing.query.filter(
            JobListing.scraped_at < fourteen_days_ago,
            JobListing.is_active == True
        ).update({'is_active': False})

        db.session.commit()

        return f"Deactivated {updated} old job listings"

    except Exception as e:
        db.session.rollback()
        return f"Error deactivating listings: {str(e)}"
