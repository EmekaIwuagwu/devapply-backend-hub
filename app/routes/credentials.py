from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.platform_credential import PlatformCredential
from app.utils.auth_utils import create_response, error_response

credentials_bp = Blueprint('credentials', __name__)


@credentials_bp.route('', methods=['GET'])
@jwt_required()
def get_credentials():
    """Get all platform credentials for user"""
    try:
        user_id = get_jwt_identity()

        credentials = PlatformCredential.query.filter_by(user_id=user_id).all()

        return create_response(
            data={
                'credentials': [cred.to_dict(include_password=False) for cred in credentials]
            }
        )

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@credentials_bp.route('', methods=['POST'])
@jwt_required()
def add_credential():
    """Add or update platform credential"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        platform = data.get('platform')
        username = data.get('username')
        password = data.get('password')

        if not platform or not username or not password:
            return error_response('VALIDATION_ERROR', 'Platform, username, and password are required', status_code=400)

        # Check if credential already exists
        existing = PlatformCredential.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()

        if existing:
            # Update existing
            existing.username = username
            existing.set_password(password)
            existing.is_active = True
            db.session.commit()

            return create_response(
                data={'credential': existing.to_dict(include_password=False)},
                message='Credential updated successfully'
            )
        else:
            # Create new
            credential = PlatformCredential(
                user_id=user_id,
                platform=platform,
                username=username
            )
            credential.set_password(password)

            db.session.add(credential)
            db.session.commit()

            return create_response(
                data={'credential': credential.to_dict(include_password=False)},
                message='Credential added successfully',
                status_code=201
            )

    except Exception as e:
        db.session.rollback()
        return error_response('SAVE_FAILED', str(e), status_code=500)


@credentials_bp.route('/<platform>', methods=['DELETE'])
@jwt_required()
def delete_credential(platform):
    """Delete platform credential"""
    try:
        user_id = get_jwt_identity()

        credential = PlatformCredential.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()

        if not credential:
            return error_response('NOT_FOUND', 'Credential not found', status_code=404)

        db.session.delete(credential)
        db.session.commit()

        return create_response(message='Credential deleted successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('DELETE_FAILED', str(e), status_code=500)


@credentials_bp.route('/<platform>/verify', methods='POST'])
@jwt_required()
def verify_credential(platform):
    """Verify platform credential"""
    try:
        user_id = get_jwt_identity()

        credential = PlatformCredential.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()

        if not credential:
            return error_response('NOT_FOUND', 'Credential not found', status_code=404)

        # TODO: Implement actual verification by attempting login
        # For now, just mark as verified
        credential.verify_credentials()

        return create_response(
            data={'credential': credential.to_dict(include_password=False)},
            message='Credential verified successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('VERIFICATION_FAILED', str(e), status_code=500)
