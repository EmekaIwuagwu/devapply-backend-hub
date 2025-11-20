import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from app import db


class JobSearchConfig(db.Model):
    """Job search configuration model"""
    __tablename__ = 'job_search_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)

    # Configuration metadata
    config_name = db.Column(db.String(255))
    platforms = db.Column(JSONB, default=list, server_default='[]')  # Array of platform slugs/IDs

    # Primary job search configuration
    primary_job_title = db.Column(db.String(255))
    primary_location = db.Column(db.String(255))
    primary_job_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    primary_min_salary = db.Column(db.Integer)
    primary_max_salary = db.Column(db.Integer)
    primary_experience_level = db.Column(db.String(50))
    primary_remote_preference = db.Column(db.String(50))  # remote, hybrid, onsite
    primary_keywords = db.Column(JSONB, default=list, server_default='[]')
    primary_resume_id = db.Column(db.String(36), db.ForeignKey('resumes.id'))

    # Secondary job search configuration
    secondary_job_title = db.Column(db.String(255))
    secondary_location = db.Column(db.String(255))
    secondary_job_type = db.Column(db.String(50))
    secondary_min_salary = db.Column(db.Integer)
    secondary_max_salary = db.Column(db.Integer)
    secondary_experience_level = db.Column(db.String(50))
    secondary_remote_preference = db.Column(db.String(50))
    secondary_keywords = db.Column(JSONB, default=list, server_default='[]')
    secondary_resume_id = db.Column(db.String(36), db.ForeignKey('resumes.id'))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    primary_resume = db.relationship('Resume', foreign_keys=[primary_resume_id])
    secondary_resume = db.relationship('Resume', foreign_keys=[secondary_resume_id])

    def to_dict(self):
        """Convert config to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'config_name': self.config_name,
            'platforms': self.platforms or [],
            'primary_job_title': self.primary_job_title,
            'primary_location': self.primary_location,
            'primary_job_type': self.primary_job_type,
            'primary_min_salary': self.primary_min_salary,
            'primary_max_salary': self.primary_max_salary,
            'primary_experience_level': self.primary_experience_level,
            'primary_remote_preference': self.primary_remote_preference,
            'primary_keywords': self.primary_keywords or [],
            'primary_resume_id': self.primary_resume_id,
            'secondary_job_title': self.secondary_job_title,
            'secondary_location': self.secondary_location,
            'secondary_job_type': self.secondary_job_type,
            'secondary_min_salary': self.secondary_min_salary,
            'secondary_max_salary': self.secondary_max_salary,
            'secondary_experience_level': self.secondary_experience_level,
            'secondary_remote_preference': self.secondary_remote_preference,
            'secondary_keywords': self.secondary_keywords or [],
            'secondary_resume_id': self.secondary_resume_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<JobSearchConfig {self.id}>'
