from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.models.subscription import Subscription
from app.utils.validators import validate_email, validate_password, validate_phone, validate_skills, validate_file_size
from app.utils.auth_utils import generate_tokens, create_response, error_response
from app.utils.file_utils import get_file_size_from_base64, clean_base64

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return error_response('VALIDATION_ERROR', 'Email and password are required', status_code=400)

        # Validate email
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            return error_response('INVALID_EMAIL', error, status_code=400)

        # Validate password
        is_valid, error = validate_password(data['password'])
        if not is_valid:
            return error_response('INVALID_PASSWORD', error, status_code=400)

        # Check if user already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return error_response('USER_EXISTS', 'User with this email already exists', status_code=400)

        # Create new user
        user = User(
            email=data['email'].lower(),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.flush()

        # Create free subscription for new user
        subscription = Subscription(
            user_id=user.id,
            plan_type='free',
            status='active',
            applications_limit=10,
            applications_used=0
        )
        db.session.add(subscription)
        db.session.commit()

        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)

        return create_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            },
            message='User registered successfully',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return error_response('REGISTRATION_FAILED', str(e), status_code=500)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    """Login user with email and password"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return error_response('VALIDATION_ERROR', 'Email and password are required', status_code=400)

        # Find user
        user = User.query.filter_by(email=data['email'].lower()).first()
        if not user or not user.check_password(data['password']):
            return error_response('INVALID_CREDENTIALS', 'Invalid email or password', status_code=401)

        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)

        return create_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            },
            message='Login successful'
        )

    except Exception as e:
        return error_response('LOGIN_FAILED', str(e), status_code=500)


@auth_bp.route('/google', methods=['POST'])
def google_login():
    """OAuth login with Google"""
    try:
        data = request.get_json()
        oauth_id = data.get('oauth_id')
        email = data.get('email')
        full_name = data.get('full_name')

        if not oauth_id or not email:
            return error_response('VALIDATION_ERROR', 'OAuth ID and email are required', status_code=400)

        # Check if user exists
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Create new user
            user = User(
                email=email.lower(),
                full_name=full_name,
                oauth_provider='google',
                oauth_id=oauth_id
            )
            db.session.add(user)
            db.session.flush()

            # Create free subscription
            subscription = Subscription(
                user_id=user.id,
                plan_type='free',
                status='active',
                applications_limit=10,
                applications_used=0
            )
            db.session.add(subscription)
            db.session.commit()
        else:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = oauth_id
                db.session.commit()

        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)

        return create_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            },
            message='Login successful'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('OAUTH_LOGIN_FAILED', str(e), status_code=500)


@auth_bp.route('/github', methods=['POST'])
def github_login():
    """OAuth login with GitHub"""
    try:
        data = request.get_json()
        oauth_id = data.get('oauth_id')
        email = data.get('email')
        full_name = data.get('full_name')

        if not oauth_id or not email:
            return error_response('VALIDATION_ERROR', 'OAuth ID and email are required', status_code=400)

        # Check if user exists
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Create new user
            user = User(
                email=email.lower(),
                full_name=full_name,
                oauth_provider='github',
                oauth_id=oauth_id
            )
            db.session.add(user)
            db.session.flush()

            # Create free subscription
            subscription = Subscription(
                user_id=user.id,
                plan_type='free',
                status='active',
                applications_limit=10,
                applications_used=0
            )
            db.session.add(subscription)
            db.session.commit()
        else:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'github'
                user.oauth_id = oauth_id
                db.session.commit()

        # Generate tokens
        access_token, refresh_token = generate_tokens(user.id)

        return create_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            },
            message='Login successful'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('OAUTH_LOGIN_FAILED', str(e), status_code=500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        return create_response(data={'user': user.to_dict()})

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        data = request.get_json()

        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            is_valid, error = validate_phone(data['phone'])
            if not is_valid:
                return error_response('INVALID_PHONE', error, status_code=400)
            user.phone = data['phone']
        if 'location' in data:
            user.location = data['location']
        if 'linkedin_url' in data:
            user.linkedin_url = data['linkedin_url']
        if 'github_url' in data:
            user.github_url = data['github_url']
        if 'portfolio_url' in data:
            user.portfolio_url = data['portfolio_url']
        if 'current_role' in data:
            user.current_role = data['current_role']
        if 'years_experience' in data:
            user.years_experience = data['years_experience']
        if 'preferred_job_type' in data:
            user.preferred_job_type = data['preferred_job_type']
        if 'salary_expectations' in data:
            user.salary_expectations = data['salary_expectations']
        if 'professional_bio' in data:
            user.professional_bio = data['professional_bio']
        if 'skills' in data:
            is_valid, error = validate_skills(data['skills'])
            if not is_valid:
                return error_response('INVALID_SKILLS', error, status_code=400)
            user.skills = data['skills']

        db.session.commit()

        return create_response(
            data={'user': user.to_dict()},
            message='Profile updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPDATE_FAILED', str(e), status_code=500)


@auth_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar (base64)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        data = request.get_json()
        avatar_base64 = data.get('avatar_base64')

        if not avatar_base64:
            return error_response('VALIDATION_ERROR', 'Avatar data is required', status_code=400)

        # Clean and validate base64
        avatar_base64 = clean_base64(avatar_base64)

        # Check file size
        file_size = get_file_size_from_base64(avatar_base64)
        from app.config import Config
        is_valid, error = validate_file_size(file_size, Config.MAX_AVATAR_SIZE)
        if not is_valid:
            return error_response('FILE_TOO_LARGE', error, status_code=400)

        user.avatar_base64 = avatar_base64
        db.session.commit()

        return create_response(
            data={'user': user.to_dict()},
            message='Avatar uploaded successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPLOAD_FAILED', str(e), status_code=500)


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return error_response('VALIDATION_ERROR', 'Current and new password are required', status_code=400)

        # Verify current password
        if not user.check_password(current_password):
            return error_response('INVALID_PASSWORD', 'Current password is incorrect', status_code=400)

        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            return error_response('INVALID_PASSWORD', error, status_code=400)

        user.set_password(new_password)
        db.session.commit()

        return create_response(message='Password changed successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('PASSWORD_CHANGE_FAILED', str(e), status_code=500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        from flask_jwt_extended import create_access_token
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)

        return create_response(
            data={'access_token': access_token},
            message='Token refreshed successfully'
        )

    except Exception as e:
        return error_response('REFRESH_FAILED', str(e), status_code=500)

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Request password reset email"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return error_response('VALIDATION_ERROR', 'Email is required', status_code=400)

        # Find user
        user = User.query.filter_by(email=email.lower()).first()
        
        # Don't reveal if user exists or not (security best practice)
        if not user:
            return create_response(
                message='If an account with that email exists, a password reset link has been sent'
            )

        # Generate reset token
        token = user.generate_password_reset_token()
        db.session.commit()

        # Send password reset email
        from app.utils.email_service import email_service
        reset_url = f"{request.host_url}reset-password?token={token}"
        
        email_service.send_password_reset(user.email, {
            'user_name': user.full_name or 'User',
            'reset_url': reset_url,
            'token': token
        })

        return create_response(
            message='If an account with that email exists, a password reset link has been sent'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('PASSWORD_RESET_REQUEST_FAILED', str(e), status_code=500)


@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return error_response('VALIDATION_ERROR', 'Token and new password are required', status_code=400)

        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            return error_response('INVALID_PASSWORD', error, status_code=400)

        # Find user with this token
        user = User.query.filter_by(password_reset_token=token).first()
        if not user:
            return error_response('INVALID_TOKEN', 'Invalid or expired reset token', status_code=400)

        # Verify token
        if not user.verify_password_reset_token(token, expiry_hours=1):
            return error_response('INVALID_TOKEN', 'Invalid or expired reset token', status_code=400)

        # Set new password
        user.set_password(new_password)
        user.clear_password_reset_token()
        db.session.commit()

        return create_response(message='Password reset successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('PASSWORD_RESET_FAILED', str(e), status_code=500)


@auth_bp.route('/send-verification-email', methods=['POST'])
@jwt_required()
def send_verification_email():
    """Send email verification link"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        if user.email_verified:
            return error_response('ALREADY_VERIFIED', 'Email is already verified', status_code=400)

        # Generate verification token
        token = user.generate_email_verification_token()
        db.session.commit()

        # Send verification email
        from app.utils.email_service import email_service
        verification_url = f"{request.host_url}verify-email?token={token}"
        
        email_service.send_email_verification(user.email, {
            'user_name': user.full_name or 'User',
            'verification_url': verification_url,
            'token': token
        })

        return create_response(message='Verification email sent successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('VERIFICATION_EMAIL_FAILED', str(e), status_code=500)


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify email with token"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return error_response('VALIDATION_ERROR', 'Verification token is required', status_code=400)

        # Find user with this token
        user = User.query.filter_by(email_verification_token=token).first()
        if not user:
            return error_response('INVALID_TOKEN', 'Invalid or expired verification token', status_code=400)

        # Verify token
        if not user.verify_email_token(token, expiry_hours=24):
            return error_response('INVALID_TOKEN', 'Invalid or expired verification token', status_code=400)

        db.session.commit()

        return create_response(
            data={'user': user.to_dict()},
            message='Email verified successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('EMAIL_VERIFICATION_FAILED', str(e), status_code=500)


@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Delete user account permanently"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        data = request.get_json() or {}
        password = data.get('password')

        # Require password confirmation for non-OAuth users
        if user.password_hash and not password:
            return error_response('VALIDATION_ERROR', 'Password confirmation is required', status_code=400)

        if user.password_hash and not user.check_password(password):
            return error_response('INVALID_PASSWORD', 'Incorrect password', status_code=400)

        # Delete user (cascade will handle related records)
        user_email = user.email
        db.session.delete(user)
        db.session.commit()

        # Send account deletion confirmation email
        from app.utils.email_service import email_service
        email_service.send_account_deleted(user_email, {
            'user_name': user.full_name or 'User'
        })

        return create_response(message='Account deleted successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('ACCOUNT_DELETION_FAILED', str(e), status_code=500)
