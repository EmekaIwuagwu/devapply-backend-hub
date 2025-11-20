import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from app import db


class ActivityLog(db.Model):
    """Activity log model for tracking admin and system activities"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # 'user_updated', 'video_uploaded', etc.
    entity_type = db.Column(db.String(50))  # 'user', 'video', 'payment', 'settings'
    entity_id = db.Column(db.String(36))  # ID of the affected entity
    description = db.Column(db.Text, nullable=False)  # Human-readable description
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    changes = db.Column(JSONB, default=dict, server_default='{}')  # Track what changed (before/after)
    status = db.Column(db.String(20), default='success')  # 'success', 'failed', 'warning'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    admin = db.relationship('User', foreign_keys=[admin_id], backref='activity_logs')

    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_email': self.admin.email if self.admin else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'changes': self.changes or {},
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.admin_id}>'
