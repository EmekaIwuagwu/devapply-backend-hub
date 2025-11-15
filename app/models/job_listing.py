import uuid
from datetime import datetime
from app import db


class JobListing(db.Model):
    """Job listing model for cached job postings"""
    __tablename__ = 'job_listings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(50), nullable=False, index=True)
    external_id = db.Column(db.String(255), nullable=False, index=True)  # Job ID from platform
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False, index=True)
    location = db.Column(db.String(255))
    salary_range = db.Column(db.String(100))
    job_type = db.Column(db.String(100))  # Full-time, Part-time, Contract, etc.
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    job_url = db.Column(db.Text, nullable=False)
    posted_date = db.Column(db.DateTime)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Create composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('platform', 'external_id', name='unique_job_per_platform'),
    )

    def to_dict(self):
        """Convert job listing to dictionary"""
        return {
            'id': self.id,
            'platform': self.platform,
            'external_id': self.external_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'location': self.location,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'description': self.description,
            'requirements': self.requirements,
            'job_url': self.job_url,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<JobListing {self.platform} - {self.company_name} - {self.job_title}>'
