from datetime import datetime
from app import db


class Settings(db.Model):
    """Settings model for system-wide configuration (singleton)"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True, default=1)  # Always 1 for singleton

    # General Settings
    site_name = db.Column(db.String(255), default='DevApply')
    site_description = db.Column(db.Text)
    contact_email = db.Column(db.String(255))
    support_phone = db.Column(db.String(20))
    logo_base64 = db.Column(db.Text)

    # Notification Settings
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    system_alerts_enabled = db.Column(db.Boolean, default=True)
    admin_notification_email = db.Column(db.String(255))
    low_balance_threshold = db.Column(db.Integer, default=100)  # Alert when credits/applications low

    # Security Settings
    session_timeout_minutes = db.Column(db.Integer, default=1440)  # 24 hours
    max_login_attempts = db.Column(db.Integer, default=5)
    password_min_length = db.Column(db.Integer, default=8)
    require_email_verification = db.Column(db.Boolean, default=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)

    # System Settings
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text)
    api_rate_limit_per_hour = db.Column(db.Integer, default=1000)
    max_file_upload_mb = db.Column(db.Integer, default=50)
    allowed_file_types = db.Column(db.JSON, default=list)  # ['pdf', 'doc', 'docx', etc.]

    # Automation Settings
    max_applications_per_user_per_day = db.Column(db.Integer, default=50)
    auto_cleanup_days = db.Column(db.Integer, default=90)  # Clean old data after N days

    # Feature Flags
    linkedin_integration_enabled = db.Column(db.Boolean, default=True)
    indeed_integration_enabled = db.Column(db.Boolean, default=True)
    ai_matching_enabled = db.Column(db.Boolean, default=True)
    video_tutorials_enabled = db.Column(db.Boolean, default=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(36), db.ForeignKey('users.id'))

    def to_dict(self):
        """Convert settings to dictionary"""
        return {
            'id': self.id,
            'general': {
                'site_name': self.site_name,
                'site_description': self.site_description,
                'contact_email': self.contact_email,
                'support_phone': self.support_phone,
                'logo_base64': self.logo_base64
            },
            'notifications': {
                'email_notifications_enabled': self.email_notifications_enabled,
                'system_alerts_enabled': self.system_alerts_enabled,
                'admin_notification_email': self.admin_notification_email,
                'low_balance_threshold': self.low_balance_threshold
            },
            'security': {
                'session_timeout_minutes': self.session_timeout_minutes,
                'max_login_attempts': self.max_login_attempts,
                'password_min_length': self.password_min_length,
                'require_email_verification': self.require_email_verification,
                'two_factor_enabled': self.two_factor_enabled
            },
            'system': {
                'maintenance_mode': self.maintenance_mode,
                'maintenance_message': self.maintenance_message,
                'api_rate_limit_per_hour': self.api_rate_limit_per_hour,
                'max_file_upload_mb': self.max_file_upload_mb,
                'allowed_file_types': self.allowed_file_types or []
            },
            'automation': {
                'max_applications_per_user_per_day': self.max_applications_per_user_per_day,
                'auto_cleanup_days': self.auto_cleanup_days
            },
            'features': {
                'linkedin_integration_enabled': self.linkedin_integration_enabled,
                'indeed_integration_enabled': self.indeed_integration_enabled,
                'ai_matching_enabled': self.ai_matching_enabled,
                'video_tutorials_enabled': self.video_tutorials_enabled
            },
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

    @staticmethod
    def get_settings():
        """Get or create singleton settings instance"""
        settings = Settings.query.filter_by(id=1).first()
        if not settings:
            settings = Settings(id=1)
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self):
        return f'<Settings {self.site_name}>'
