"""
Response utility functions for consistent API responses
"""
from flask import jsonify


def create_response(data=None, message=None, status_code=200):
    """
    Create a successful API response

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default: 200)

    Returns:
        Flask JSON response
    """
    response = {
        'success': True
    }

    if data is not None:
        response['data'] = data

    if message:
        response['message'] = message

    return jsonify(response), status_code


def error_response(message, code=None, details=None, status_code=400):
    """
    Create an error API response

    Args:
        message: Error message
        code: Error code (optional)
        details: Additional error details (optional)
        status_code: HTTP status code (default: 400)

    Returns:
        Flask JSON response
    """
    response = {
        'success': False,
        'error': {
            'message': message
        }
    }

    if code:
        response['error']['code'] = code

    if details:
        response['error']['details'] = details

    return jsonify(response), status_code
