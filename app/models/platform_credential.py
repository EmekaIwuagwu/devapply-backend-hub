import uuid
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from app import db


class PlatformCredential(db.Model):
    """Platform credentials model for storing encrypted login credentials"""
    __tablename__ = 'platform_credentials'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False, index=True)  # 'linkedin', 'indeed', etc.
    username_encrypted = db.Column(db.Text)  # Encrypted username/email
    encrypted_password = db.Column(db.Text, nullable=False)  # Encrypted password (matches DB column name)
    cookies_encrypted = db.Column(db.Text)  # Encrypted session cookies (JSON)
    is_verified = db.Column(db.Boolean, default=False)  # Match DB column name
    last_verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Create unique constraint on user_id and platform
    __table_args__ = (
        db.UniqueConstraint('user_id', 'platform', name='unique_user_platform_credential'),
    )

    @staticmethod
    def get_cipher():
        """Get Fernet cipher for encryption/decryption"""
        key = os.getenv('CREDENTIALS_ENCRYPTION_KEY')
        if not key:
            # Generate a key if not set (for development only)
            key = Fernet.generate_key().decode()
            print(f"WARNING: Using generated encryption key. Set CREDENTIALS_ENCRYPTION_KEY in production!")

        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        return Fernet(key)

    def set_username(self, username):
        """Encrypt and store username"""
        cipher = self.get_cipher()
        self.username_encrypted = cipher.encrypt(username.encode()).decode()

    def get_username(self):
        """Decrypt and return username"""
        if not self.username_encrypted:
            return None
        cipher = self.get_cipher()
        return cipher.decrypt(self.username_encrypted.encode()).decode()

    def set_password(self, password):
        """Encrypt and store password"""
        cipher = self.get_cipher()
        self.encrypted_password = cipher.encrypt(password.encode()).decode()

    def get_password(self):
        """Decrypt and return password"""
        cipher = self.get_cipher()
        return cipher.decrypt(self.encrypted_password.encode()).decode()

    def set_cookies(self, cookies_dict):
        """
        Encrypt and store session cookies
        Args:
            cookies_dict (dict): Dictionary of cookie name/value pairs
        """
        cipher = self.get_cipher()
        cookies_json = json.dumps(cookies_dict)
        self.cookies_encrypted = cipher.encrypt(cookies_json.encode()).decode()

    def get_cookies(self):
        """
        Decrypt and return cookies as dictionary
        Returns:
            dict: Cookie name/value pairs or None
        """
        if not self.cookies_encrypted:
            return None
        cipher = self.get_cipher()
        cookies_json = cipher.decrypt(self.cookies_encrypted.encode()).decode()
        return json.loads(cookies_json)

    def has_cookies(self):
        """Check if cookies are stored"""
        return bool(self.cookies_encrypted)

    def verify_credentials(self):
        """
        Verify credentials are still valid
        TODO: Implement platform-specific verification
        """
        # This would test login to the platform
        self.last_verified_at = datetime.utcnow()
        db.session.commit()
        return True

    def to_dict(self, include_password=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'username': self.get_username(),  # Decrypt username for display
            'is_verified': self.is_verified,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_password:
            # Only include password when explicitly requested (for automation tasks)
            data['password'] = self.get_password()

        return data

    def __repr__(self):
        username = self.get_username() if self.username_encrypted else 'N/A'
        return f'<PlatformCredential {self.platform} - {username}>'
