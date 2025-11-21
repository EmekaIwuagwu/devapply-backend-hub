#!/usr/bin/env python3
"""
Test script to trigger immediate job application
"""
import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.job_search_config import JobSearchConfig
from app.tasks.immediate_applicator import start_immediate_applications

def main():
    app = create_app()

    with app.app_context():
        # Find first user
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return

        print(f"✅ Found user: {user.email}")

        # Find their job search config
        config = JobSearchConfig.query.filter_by(user_id=user.id).first()
        if not config:
            print("❌ No job search config found for user")
            return

        print(f"✅ Found job search config: {config.primary_job_title} in {config.primary_location}")
        print(f"   Platforms: {config.platforms}")

        # Trigger the immediate application
        print("\n🚀 Triggering immediate application task...")
        print("   This will initialize browser, login, and search for jobs")
        print("   Check logs/automation.log for detailed progress\n")

        result = start_immediate_applications.delay(user_id=user.id, config_id=config.id)

        print(f"✅ Task triggered successfully!")
        print(f"   Task ID: {result.id}")
        print(f"\n📋 Monitor progress with:")
        print(f"   tail -f logs/automation.log")
        print(f"   tail -f logs/celery-worker.log")

if __name__ == '__main__':
    main()
