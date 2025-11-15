import uuid
from datetime import datetime
from app import db


class Application(db.Model):
    """Job application model"""
    __tablename__ = 'applications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(100))  # 'Full-time', 'Remote', etc.
    location = db.Column(db.String(255))
    salary_range = db.Column(db.String(100))
    status = db.Column(db.String(20), default='sent', index=True)  # 'sent', 'viewed', 'interview', 'rejected'
    platform = db.Column(db.String(50), nullable=False)  # 'LinkedIn', 'Indeed', etc.
    job_url = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_status_update = db.Column(db.DateTime, default=datetime.utcnow)
    resume_used_id = db.Column(db.String(36), db.ForeignKey('resumes.id'))
    cover_letter = db.Column(db.Text)
    notes = db.Column(db.Text)

    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_type': self.job_type,
            'location': self.location,
            'salary_range': self.salary_range,
            'status': self.status,
            'platform': self.platform,
            'job_url': self.job_url,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'last_status_update': self.last_status_update.isoformat() if self.last_status_update else None,
            'resume_used_id': self.resume_used_id,
            'cover_letter': self.cover_letter,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<Application {self.company_name} - {self.job_title}>'
