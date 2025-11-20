from datetime import datetime
from functools import wraps
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from app.models import User


def generate_tokens(user_id):
    """Generate access and refresh tokens for a user"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return access_token, refresh_token


def create_response(data=None, message=None, meta=None, status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'data': data or {},
        'meta': meta or {'timestamp': datetime.utcnow().isoformat()}
    }
    if message:
        response['message'] = message
    return jsonify(response), status_code


def error_response(code, message, details=None, status_code=400):
    """Create a standardized error response"""
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details or {}
        }
    }
    return jsonify(response), status_code


def admin_required(allowed_roles=None):
    """
    Decorator to require admin authentication for routes.

    Args:
        allowed_roles: List of allowed roles (default: ['admin', 'moderator'])

    Usage:
        @admin_required()
        def some_route():
            pass

        @admin_required(allowed_roles=['admin'])  # Only admins
        def another_route():
            pass
    """
    if allowed_roles is None:
        allowed_roles = ['admin', 'moderator']

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT token
            verify_jwt_in_request()

            # Get user ID from token
            user_id = get_jwt_identity()

            # Get user from database
            user = User.query.get(user_id)

            if not user:
                return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

            # Check if user has required role
            if user.role not in allowed_roles:
                return error_response(
                    'INSUFFICIENT_PERMISSIONS',
                    'You do not have permission to access this resource',
                    details={'required_roles': allowed_roles, 'your_role': user.role},
                    status_code=403
                )

            return fn(*args, **kwargs)

        return wrapper
    return decorator
