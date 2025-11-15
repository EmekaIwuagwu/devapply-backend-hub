from datetime import datetime
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token


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
