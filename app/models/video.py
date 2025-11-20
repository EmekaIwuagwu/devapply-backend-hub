import uuid
from datetime import datetime
from app import db


class Video(db.Model):
    """Video model for storing tutorial and help videos"""
    __tablename__ = 'videos'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    video_base64 = db.Column(db.Text, nullable=False)  # Base64 encoded video file
    thumbnail_base64 = db.Column(db.Text)  # Base64 encoded thumbnail image
    file_size = db.Column(db.Integer)  # File size in bytes
    duration = db.Column(db.Integer)  # Duration in seconds
    category = db.Column(db.String(100))  # 'tutorial', 'demo', 'help', etc.
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_videos')

    def to_dict(self, include_video=False):
        """Convert video to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'thumbnail_base64': self.thumbnail_base64,
            'file_size': self.file_size,
            'duration': self.duration,
            'category': self.category,
            'is_active': self.is_active,
            'view_count': self.view_count,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Only include video data if explicitly requested (to save bandwidth)
        if include_video:
            data['video_base64'] = self.video_base64

        return data

    def __repr__(self):
        return f'<Video {self.title}>'
