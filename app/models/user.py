import uuid
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    portfolio_url = db.Column(db.String(500))
    current_role = db.Column(db.String(255))
    years_experience = db.Column(db.Integer)
    preferred_job_type = db.Column(db.String(100))
    salary_expectations = db.Column(db.Integer)
    professional_bio = db.Column(db.Text)
    skills = db.Column(db.JSON, default=list)
    avatar_base64 = db.Column(db.Text)
    oauth_provider = db.Column(db.String(20))  # 'google' or 'github'
    oauth_id = db.Column(db.String(255))

    # User role for admin access control
    role = db.Column(db.String(20), default='user', nullable=False, index=True)  # 'user', 'admin', 'moderator'

    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), unique=True, nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)

    # Password reset
    password_reset_token = db.Column(db.String(255), unique=True, nullable=True)
    password_reset_sent_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    search_configs = db.relationship('JobSearchConfig', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_email_verification_token(self):
        """Generate a secure token for email verification"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = datetime.utcnow()
        return self.email_verification_token

    def verify_email_token(self, token, expiry_hours=24):
        """Verify email verification token"""
        if not self.email_verification_token or self.email_verification_token != token:
            return False

        # Check if token has expired
        if self.email_verification_sent_at:
            expiry_time = self.email_verification_sent_at + timedelta(hours=expiry_hours)
            if datetime.utcnow() > expiry_time:
                return False

        # Mark email as verified
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_sent_at = None
        return True

    def generate_password_reset_token(self):
        """Generate a secure token for password reset"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_sent_at = datetime.utcnow()
        return self.password_reset_token

    def verify_password_reset_token(self, token, expiry_hours=1):
        """Verify password reset token"""
        if not self.password_reset_token or self.password_reset_token != token:
            return False

        # Check if token has expired
        if self.password_reset_sent_at:
            expiry_time = self.password_reset_sent_at + timedelta(hours=expiry_hours)
            if datetime.utcnow() > expiry_time:
                return False

        return True

    def clear_password_reset_token(self):
        """Clear password reset token after successful reset"""
        self.password_reset_token = None
        self.password_reset_sent_at = None

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'email_verified': self.email_verified,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'current_role': self.current_role,
            'years_experience': self.years_experience,
            'preferred_job_type': self.preferred_job_type,
            'salary_expectations': self.salary_expectations,
            'professional_bio': self.professional_bio,
            'skills': self.skills or [],
            'avatar_base64': self.avatar_base64,
            'oauth_provider': self.oauth_provider,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        return data

    def __repr__(self):
        return f'<User {self.email}>'
