import uuid
from datetime import datetime
from app import db


class JobQueue(db.Model):
    """Job queue model for managing automated applications"""
    __tablename__ = 'job_queue'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    job_search_config_id = db.Column(db.String(36), db.ForeignKey('job_search_configs.id'))
    platform = db.Column(db.String(50), nullable=False)
    job_listing_id = db.Column(db.String(36), db.ForeignKey('job_listings.id'))
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    job_url = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, applied, failed, skipped
    priority = db.Column(db.Integer, default=5, index=True)  # 1-10, higher = more important
    match_score = db.Column(db.Float, default=0.0)  # 0-100
    scheduled_for = db.Column(db.DateTime)
    attempted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    job_listing = db.relationship('JobListing', backref='queue_items', lazy='joined')

    def to_dict(self):
        """Convert job queue item to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_search_config_id': self.job_search_config_id,
            'platform': self.platform,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_url': self.job_url,
            'status': self.status,
            'priority': self.priority,
            'match_score': self.match_score,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<JobQueue {self.company_name} - {self.job_title} ({self.status})>'
