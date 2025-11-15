from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.subscription import Subscription, Payment
from app.utils.auth_utils import create_response, error_response

subscription_bp = Blueprint('subscription', __name__)

# Plan definitions
PLANS = {
    'free': {
        'name': 'Free',
        'applications_limit': 10,
        'price': 0,
        'features': ['10 job applications', 'Basic search', 'Email notifications']
    },
    'pro': {
        'name': 'Professional',
        'applications_limit': 100,
        'price_monthly': 29.99,
        'price_yearly': 299.99,
        'features': ['100 job applications', 'Advanced search', 'Priority support', 'Resume templates']
    },
    'max': {
        'name': 'Maximum',
        'applications_limit': -1,  # Unlimited
        'price_monthly': 49.99,
        'price_yearly': 499.99,
        'features': ['Unlimited applications', 'AI-powered matching', 'Dedicated support', 'Premium templates']
    }
}


@subscription_bp.route('', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user subscription"""
    try:
        user_id = get_jwt_identity()
        subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()

        if not subscription:
            return error_response('SUBSCRIPTION_NOT_FOUND', 'No active subscription found', status_code=404)

        return create_response(data={'subscription': subscription.to_dict()})

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@subscription_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans"""
    return create_response(data={'plans': PLANS})


@subscription_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade_plan():
    """Upgrade subscription plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        plan_type = data.get('plan_type')
        billing_cycle = data.get('billing_cycle', 'monthly')

        if plan_type not in ['pro', 'max']:
            return error_response('INVALID_PLAN', 'Invalid plan type', status_code=400)

        if billing_cycle not in ['monthly', 'yearly']:
            return error_response('INVALID_BILLING_CYCLE', 'Invalid billing cycle', status_code=400)

        # Get current subscription
        current_sub = Subscription.query.filter_by(user_id=user_id, status='active').first()

        # Calculate amount
        plan = PLANS[plan_type]
        amount = plan[f'price_{billing_cycle}']

        # Cancel current subscription if exists
        if current_sub:
            current_sub.status = 'cancelled'
            current_sub.cancelled_at = datetime.utcnow()

        # Create new subscription
        next_billing = datetime.utcnow() + timedelta(days=30 if billing_cycle == 'monthly' else 365)

        new_sub = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            status='active',
            applications_limit=plan['applications_limit'],
            applications_used=0,
            billing_cycle=billing_cycle,
            amount=amount,
            currency='USD',
            next_billing_date=next_billing.date()
        )

        db.session.add(new_sub)
        db.session.commit()

        return create_response(
            data={'subscription': new_sub.to_dict()},
            message='Plan upgraded successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPGRADE_FAILED', str(e), status_code=500)


@subscription_bp.route('/downgrade', methods=['POST'])
@jwt_required()
def downgrade_plan():
    """Downgrade subscription plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        plan_type = data.get('plan_type', 'free')

        # Get current subscription
        current_sub = Subscription.query.filter_by(user_id=user_id, status='active').first()

        if not current_sub:
            return error_response('SUBSCRIPTION_NOT_FOUND', 'No active subscription found', status_code=404)

        # Update to new plan
        plan = PLANS[plan_type]
        current_sub.plan_type = plan_type
        current_sub.applications_limit = plan['applications_limit']

        if plan_type == 'free':
            current_sub.amount = 0
            current_sub.billing_cycle = None
            current_sub.next_billing_date = None

        db.session.commit()

        return create_response(
            data={'subscription': current_sub.to_dict()},
            message='Plan downgraded successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('DOWNGRADE_FAILED', str(e), status_code=500)


@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel subscription"""
    try:
        user_id = get_jwt_identity()

        subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()

        if not subscription:
            return error_response('SUBSCRIPTION_NOT_FOUND', 'No active subscription found', status_code=404)

        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
        db.session.commit()

        return create_response(
            data={'subscription': subscription.to_dict()},
            message='Subscription cancelled successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('CANCEL_FAILED', str(e), status_code=500)


@subscription_bp.route('/payment/method', methods=['POST'])
@jwt_required()
def add_payment_method():
    """Add or update payment method"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # In a real implementation, this would integrate with a payment processor
        # For now, we'll just return success
        return create_response(
            data={
                'payment_method': {
                    'last4': data.get('last4'),
                    'expiry': data.get('expiry'),
                    'brand': data.get('brand')
                }
            },
            message='Payment method added successfully'
        )

    except Exception as e:
        return error_response('PAYMENT_METHOD_FAILED', str(e), status_code=500)


@subscription_bp.route('/payment/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get billing history"""
    try:
        user_id = get_jwt_identity()

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))

        query = Payment.query.filter_by(user_id=user_id).order_by(Payment.paid_at.desc())
        total = query.count()
        payments = query.offset((page - 1) * limit).limit(limit).all()

        return create_response(
            data={
                'payments': [payment.to_dict() for payment in payments],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        )

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@subscription_bp.route('/payment/invoice/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Download invoice"""
    try:
        user_id = get_jwt_identity()
        payment = Payment.query.filter_by(id=invoice_id, user_id=user_id).first()

        if not payment:
            return error_response('INVOICE_NOT_FOUND', 'Invoice not found', status_code=404)

        return create_response(data={'payment': payment.to_dict()})

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)
