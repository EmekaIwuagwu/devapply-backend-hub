import os
from datetime import datetime, timedelta
from app import db
from app.models.application import Application


class ApplicationRateLimiter:
    """Rate limiter to prevent overwhelming job boards"""

    # Platform-specific rate limits
    PLATFORM_LIMITS = {
        'linkedin': {
            'max_per_hour': int(os.getenv('MAX_APPLICATIONS_PER_HOUR', 5)),
            'max_per_day': int(os.getenv('MAX_APPLICATIONS_PER_DAY', 20)),
            'delay_between': int(os.getenv('APPLICATION_DELAY_SECONDS', 180))  # 3 minutes
        },
        'indeed': {
            'max_per_hour': 10,
            'max_per_day': 40,
            'delay_between': 120  # 2 minutes
        },
        'glassdoor': {
            'max_per_hour': 5,
            'max_per_day': 15,
            'delay_between': 240  # 4 minutes
        },
        'default': {
            'max_per_hour': 5,
            'max_per_day': 20,
            'delay_between': 180
        }
    }

    @classmethod
    def get_platform_limits(cls, platform):
        """Get rate limits for a specific platform"""
        platform_key = platform.lower()
        return cls.PLATFORM_LIMITS.get(platform_key, cls.PLATFORM_LIMITS['default'])

    @classmethod
    def get_recent_applications(cls, user_id, platform, hours=1):
        """Get applications from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        return Application.query.filter(
            Application.user_id == user_id,
            Application.platform == platform,
            Application.applied_at >= cutoff
        ).count()

    @classmethod
    def get_last_application_time(cls, user_id, platform):
        """Get the timestamp of the last application"""
        last_app = Application.query.filter(
            Application.user_id == user_id,
            Application.platform == platform
        ).order_by(Application.applied_at.desc()).first()

        return last_app.applied_at if last_app else None

    @classmethod
    def can_apply(cls, user_id, platform):
        """
        Check if user can apply to another job on this platform
        Returns (can_apply: bool, reason: str, wait_seconds: int)
        """
        limits = cls.get_platform_limits(platform)

        # Check hourly limit
        apps_last_hour = cls.get_recent_applications(user_id, platform, hours=1)
        if apps_last_hour >= limits['max_per_hour']:
            return False, f"Hourly limit reached ({limits['max_per_hour']} applications/hour)", 3600

        # Check daily limit
        apps_last_day = cls.get_recent_applications(user_id, platform, hours=24)
        if apps_last_day >= limits['max_per_day']:
            return False, f"Daily limit reached ({limits['max_per_day']} applications/day)", 86400

        # Check minimum delay between applications
        last_app_time = cls.get_last_application_time(user_id, platform)
        if last_app_time:
            time_since_last = (datetime.utcnow() - last_app_time).total_seconds()
            if time_since_last < limits['delay_between']:
                wait_time = int(limits['delay_between'] - time_since_last)
                return False, f"Please wait {wait_time} seconds between applications", wait_time

        return True, "OK", 0

    @classmethod
    def get_wait_time(cls, user_id, platform):
        """Get how long to wait before next application"""
        can_apply, reason, wait_seconds = cls.can_apply(user_id, platform)

        if can_apply:
            return 0

        return wait_seconds

    @classmethod
    def record_application(cls, user_id, platform):
        """
        Record that an application was submitted
        Note: This is handled by creating Application record,
        but can be used for additional tracking if needed
        """
        # Could implement Redis-based tracking here for better performance
        pass

    @classmethod
    def get_user_stats(cls, user_id):
        """Get application statistics for user"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        apps_last_hour = Application.query.filter(
            Application.user_id == user_id,
            Application.applied_at >= hour_ago
        ).count()

        apps_last_day = Application.query.filter(
            Application.user_id == user_id,
            Application.applied_at >= day_ago
        ).count()

        return {
            'last_hour': apps_last_hour,
            'last_day': apps_last_day,
            'total': Application.query.filter_by(user_id=user_id).count()
        }
