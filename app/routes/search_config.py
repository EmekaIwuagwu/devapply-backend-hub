from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.job_search_config import JobSearchConfig
from app.models.resume import Resume
from app.utils.auth_utils import create_response, error_response

search_config_bp = Blueprint('search_config', __name__)


@search_config_bp.route('', methods=['POST'])
@jwt_required()
def create_or_update_config():
    """Create or update job search configuration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Check if config already exists
        config = JobSearchConfig.query.filter_by(user_id=user_id).first()

        if config:
            # Update existing config
            if 'platforms' in data:
                config.platforms = data['platforms']
            if 'primary_job_title' in data:
                config.primary_job_title = data['primary_job_title']
            if 'primary_location' in data:
                config.primary_location = data['primary_location']
            if 'primary_min_salary' in data:
                config.primary_min_salary = data['primary_min_salary']
            if 'primary_experience_level' in data:
                config.primary_experience_level = data['primary_experience_level']
            if 'primary_keywords' in data:
                config.primary_keywords = data['primary_keywords']
            if 'primary_resume_id' in data:
                # Verify resume exists and belongs to user
                resume = Resume.query.filter_by(id=data['primary_resume_id'], user_id=user_id).first()
                if resume:
                    config.primary_resume_id = data['primary_resume_id']
            if 'secondary_job_title' in data:
                config.secondary_job_title = data['secondary_job_title']
            if 'secondary_location' in data:
                config.secondary_location = data['secondary_location']
            if 'secondary_min_salary' in data:
                config.secondary_min_salary = data['secondary_min_salary']
            if 'secondary_experience_level' in data:
                config.secondary_experience_level = data['secondary_experience_level']
            if 'secondary_keywords' in data:
                config.secondary_keywords = data['secondary_keywords']
            if 'secondary_resume_id' in data:
                # Verify resume exists and belongs to user
                resume = Resume.query.filter_by(id=data['secondary_resume_id'], user_id=user_id).first()
                if resume:
                    config.secondary_resume_id = data['secondary_resume_id']
            if 'is_active' in data:
                config.is_active = data['is_active']

            db.session.commit()
            message = 'Configuration updated successfully'
            status_code = 200

        else:
            # Create new config
            config = JobSearchConfig(
                user_id=user_id,
                platforms=data.get('platforms', []),
                primary_job_title=data.get('primary_job_title'),
                primary_location=data.get('primary_location'),
                primary_min_salary=data.get('primary_min_salary'),
                primary_experience_level=data.get('primary_experience_level'),
                primary_keywords=data.get('primary_keywords', []),
                primary_resume_id=data.get('primary_resume_id'),
                secondary_job_title=data.get('secondary_job_title'),
                secondary_location=data.get('secondary_location'),
                secondary_min_salary=data.get('secondary_min_salary'),
                secondary_experience_level=data.get('secondary_experience_level'),
                secondary_keywords=data.get('secondary_keywords', []),
                secondary_resume_id=data.get('secondary_resume_id'),
                is_active=data.get('is_active', True)
            )
            db.session.add(config)
            db.session.commit()
            message = 'Configuration created successfully'
            status_code = 201

        return create_response(
            data={'config': config.to_dict()},
            message=message,
            status_code=status_code
        )

    except Exception as e:
        db.session.rollback()
        return error_response('CONFIG_FAILED', str(e), status_code=500)


@search_config_bp.route('', methods=['GET'])
@jwt_required()
def get_config():
    """Get user's job search configuration"""
    try:
        user_id = get_jwt_identity()
        config = JobSearchConfig.query.filter_by(user_id=user_id).first()

        if not config:
            # Return empty/default config instead of 404 for better UX
            return create_response(data={
                'config': None,
                'has_config': False,
                'message': 'No configuration found. Create one to get started.'
            })

        return create_response(data={
            'config': config.to_dict(),
            'has_config': True
        })

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@search_config_bp.route('/<config_id>', methods=['PUT'])
@jwt_required()
def update_config(config_id):
    """Update specific configuration"""
    try:
        user_id = get_jwt_identity()
        config = JobSearchConfig.query.filter_by(id=config_id, user_id=user_id).first()

        if not config:
            return error_response('CONFIG_NOT_FOUND', 'Configuration not found', status_code=404)

        data = request.get_json()

        # Update fields
        for key in data:
            if hasattr(config, key):
                setattr(config, key, data[key])

        db.session.commit()

        return create_response(
            data={'config': config.to_dict()},
            message='Configuration updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPDATE_FAILED', str(e), status_code=500)


@search_config_bp.route('/<config_id>', methods=['DELETE'])
@jwt_required()
def delete_config(config_id):
    """Delete configuration"""
    try:
        user_id = get_jwt_identity()
        config = JobSearchConfig.query.filter_by(id=config_id, user_id=user_id).first()

        if not config:
            return error_response('CONFIG_NOT_FOUND', 'Configuration not found', status_code=404)

        db.session.delete(config)
        db.session.commit()

        return create_response(message='Configuration deleted successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('DELETE_FAILED', str(e), status_code=500)
