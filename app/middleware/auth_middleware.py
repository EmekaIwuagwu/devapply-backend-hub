from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User


def get_current_user():
    """Get current authenticated user"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def jwt_required_custom(fn):
    """Custom JWT required decorator with error handling"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Authentication required',
                    'details': {}
                }
            }), 401
    return wrapper
