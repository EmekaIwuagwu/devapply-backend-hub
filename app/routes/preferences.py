"""
User preferences routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.utils.auth_utils import create_response, error_response

preferences_bp = Blueprint('preferences', __name__)


@preferences_bp.route('', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        # Get or create preferences
        preferences = user.preferences
        if not preferences:
            # Create default preferences
            preferences = UserPreferences(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()

        return create_response(
            data={'preferences': preferences.to_dict()},
            message='Preferences retrieved successfully'
        )

    except Exception as e:
        return error_response('PREFERENCES_FETCH_FAILED', str(e), status_code=500)


@preferences_bp.route('', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        data = request.get_json()

        # Get or create preferences
        preferences = user.preferences
        if not preferences:
            preferences = UserPreferences(user_id=user_id)
            db.session.add(preferences)

        # Update notification preferences
        if 'email_notifications_enabled' in data:
            preferences.email_notifications_enabled = data['email_notifications_enabled']
        if 'daily_summary_enabled' in data:
            preferences.daily_summary_enabled = data['daily_summary_enabled']
        if 'application_updates_enabled' in data:
            preferences.application_updates_enabled = data['application_updates_enabled']
        if 'job_matches_enabled' in data:
            preferences.job_matches_enabled = data['job_matches_enabled']
        if 'marketing_emails_enabled' in data:
            preferences.marketing_emails_enabled = data['marketing_emails_enabled']

        # Update application preferences
        if 'auto_apply_enabled' in data:
            preferences.auto_apply_enabled = data['auto_apply_enabled']
        if 'max_applications_per_day' in data:
            max_apps = data['max_applications_per_day']
            if isinstance(max_apps, int) and 1 <= max_apps <= 100:
                preferences.max_applications_per_day = max_apps
            else:
                return error_response('VALIDATION_ERROR', 'max_applications_per_day must be between 1 and 100', status_code=400)

        if 'min_match_score' in data:
            min_score = data['min_match_score']
            if isinstance(min_score, int) and 0 <= min_score <= 100:
                preferences.min_match_score = min_score
            else:
                return error_response('VALIDATION_ERROR', 'min_match_score must be between 0 and 100', status_code=400)

        # Update display preferences
        if 'timezone' in data:
            preferences.timezone = data['timezone']
        if 'language' in data:
            preferences.language = data['language']
        if 'currency' in data:
            preferences.currency = data['currency']

        db.session.commit()

        return create_response(
            data={'preferences': preferences.to_dict()},
            message='Preferences updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('PREFERENCES_UPDATE_FAILED', str(e), status_code=500)


@preferences_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset_preferences():
    """Reset preferences to default"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

        # Delete existing preferences
        if user.preferences:
            db.session.delete(user.preferences)

        # Create new default preferences
        preferences = UserPreferences(user_id=user_id)
        db.session.add(preferences)
        db.session.commit()

        return create_response(
            data={'preferences': preferences.to_dict()},
            message='Preferences reset to defaults successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('PREFERENCES_RESET_FAILED', str(e), status_code=500)
