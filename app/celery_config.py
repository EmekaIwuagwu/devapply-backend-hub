import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()


def make_celery(app=None):
    """Create Celery instance"""
    celery = Celery(
        'devapply',
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=[
            'app.tasks.job_scraper',
            'app.tasks.job_applicator',
            'app.tasks.status_checker',
            'app.tasks.notifications',
            'app.tasks.cleanup'
        ]
    )

    # Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes max per task
        task_soft_time_limit=25 * 60,  # 25 minutes soft limit
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )

    # Celery Beat Schedule
    celery.conf.beat_schedule = {
        # Scrape jobs every 6 hours for all active users
        'scrape-jobs-every-6-hours': {
            'task': 'app.tasks.job_scraper.scrape_jobs_all_users',
            'schedule': crontab(minute=0, hour='*/6'),
        },

        # Process job queue every 30 minutes
        'process-queue-every-30-min': {
            'task': 'app.tasks.job_applicator.process_job_queue',
            'schedule': crontab(minute='*/30'),
        },

        # Check application status daily at 10 AM
        'check-status-daily': {
            'task': 'app.tasks.status_checker.check_all_application_statuses',
            'schedule': crontab(hour=10, minute=0),
        },

        # Clean old data daily at 2 AM
        'cleanup-daily': {
            'task': 'app.tasks.cleanup.clean_old_jobs',
            'schedule': crontab(hour=2, minute=0),
        },

        # Send daily summaries at 8 AM
        'daily-summary': {
            'task': 'app.tasks.notifications.send_all_daily_summaries',
            'schedule': crontab(hour=8, minute=0),
        },
    }

    # If Flask app is provided, integrate with Flask
    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create celery instance for standalone worker
celery = make_celery()
