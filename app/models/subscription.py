import uuid
from datetime import datetime
from app import db


class Subscription(db.Model):
    """Subscription model for user plans"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    plan_type = db.Column(db.String(20), nullable=False, default='free')  # 'free', 'pro', 'max'
    status = db.Column(db.String(20), default='active')  # 'active', 'cancelled', 'expired'
    applications_limit = db.Column(db.Integer, default=10)
    applications_used = db.Column(db.Integer, default=0)
    billing_cycle = db.Column(db.String(20))  # 'monthly', 'yearly'
    amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')
    next_billing_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime)

    # Relationships
    payments = db.relationship('Payment', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'status': self.status,
            'applications_limit': self.applications_limit,
            'applications_used': self.applications_used,
            'billing_cycle': self.billing_cycle,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }

    def __repr__(self):
        return f'<Subscription {self.plan_type} - {self.user_id}>'


class Payment(db.Model):
    """Payment model for billing history"""
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    subscription_id = db.Column(db.String(36), db.ForeignKey('subscriptions.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_method = db.Column(db.String(50))  # last 4 digits
    payment_method_expiry = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending')  # 'paid', 'pending', 'failed'
    paid_at = db.Column(db.DateTime)
    invoice_url = db.Column(db.Text)

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_method_expiry': self.payment_method_expiry,
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'invoice_url': self.invoice_url
        }

    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency}>'
