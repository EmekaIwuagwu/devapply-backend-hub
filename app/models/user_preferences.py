"""
User preferences model for notification settings and preferences
"""
import uuid
from datetime import datetime
from app import db


class UserPreferences(db.Model):
    """User preferences for notifications and settings"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Notification preferences
    email_notifications_enabled = db.Column(db.Boolean, default=True)
    daily_summary_enabled = db.Column(db.Boolean, default=True)
    application_updates_enabled = db.Column(db.Boolean, default=True)
    job_matches_enabled = db.Column(db.Boolean, default=True)
    marketing_emails_enabled = db.Column(db.Boolean, default=False)

    # Application preferences
    auto_apply_enabled = db.Column(db.Boolean, default=True)
    max_applications_per_day = db.Column(db.Integer, default=20)
    min_match_score = db.Column(db.Integer, default=70)  # Minimum score to auto-apply (0-100)

    # Display preferences
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    currency = db.Column(db.String(3), default='USD')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('preferences', uselist=False, cascade='all, delete-orphan'))

    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_notifications_enabled': self.email_notifications_enabled,
            'daily_summary_enabled': self.daily_summary_enabled,
            'application_updates_enabled': self.application_updates_enabled,
            'job_matches_enabled': self.job_matches_enabled,
            'marketing_emails_enabled': self.marketing_emails_enabled,
            'auto_apply_enabled': self.auto_apply_enabled,
            'max_applications_per_day': self.max_applications_per_day,
            'min_match_score': self.min_match_score,
            'timezone': self.timezone,
            'language': self.language,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<UserPreferences {self.user_id}>'
