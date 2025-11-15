import uuid
from datetime import datetime
from app import db


class AutomationLog(db.Model):
    """Automation log model for tracking automation activities"""
    __tablename__ = 'automation_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    job_queue_id = db.Column(db.String(36), db.ForeignKey('job_queue.id'))
    action_type = db.Column(db.String(50), nullable=False, index=True)  # job_search, job_apply, status_update
    status = db.Column(db.String(20), nullable=False)  # success, failed, warning
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON, default=dict)  # Additional details (renamed from metadata)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert automation log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_queue_id': self.job_queue_id,
            'action_type': self.action_type,
            'status': self.status,
            'message': self.message,
            'details': self.details or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AutomationLog {self.action_type} - {self.status}>'
