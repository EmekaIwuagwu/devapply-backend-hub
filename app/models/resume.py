import uuid
from datetime import datetime
from app import db


class Resume(db.Model):
    """Resume model for storing user resumes"""
    __tablename__ = 'resumes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_base64 = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf', 'doc', 'docx'
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    is_default = db.Column(db.Boolean, default=False, index=True)
    job_type_tag = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)

    # Relationships
    applications = db.relationship('Application', backref='resume', lazy='dynamic')

    def to_dict(self, include_file=False):
        """Convert resume to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'is_default': self.is_default,
            'job_type_tag': self.job_type_tag,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }
        if include_file:
            data['file_base64'] = self.file_base64
        return data

    def __repr__(self):
        return f'<Resume {self.filename}>'
