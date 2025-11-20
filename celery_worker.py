#!/usr/bin/env python
"""
Celery worker entry point
Run with: celery -A celery_worker.celery worker --loglevel=info
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Flask app to set up application context
from app import create_app, db
from app.celery_config import make_celery

# Create Flask app
app = create_app()

# Create Celery instance with Flask context
celery = make_celery(app)

# Import all tasks to register them
from app.tasks import job_scraper, job_applicator, status_checker, notifications, cleanup, immediate_applicator

# Log registered tasks
print("=" * 80)
print("CELERY WORKER STARTING")
print("=" * 80)
print(f"Registered tasks: {list(celery.tasks.keys())}")
print("=" * 80)

if __name__ == '__main__':
    celery.start()
