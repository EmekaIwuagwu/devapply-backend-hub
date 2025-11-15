import uuid
from app import db


class Platform(db.Model):
    """Platform model for job boards"""
    __tablename__ = 'platforms'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    is_popular = db.Column(db.Boolean, default=False)
    is_enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert platform to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'is_popular': self.is_popular,
            'is_enabled': self.is_enabled
        }

    def __repr__(self):
        return f'<Platform {self.name}>'
