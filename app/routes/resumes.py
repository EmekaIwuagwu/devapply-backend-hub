from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.resume import Resume
from app.utils.auth_utils import create_response, error_response
from app.utils.file_utils import get_file_size_from_base64, get_file_extension, clean_base64
from app.utils.validators import validate_file_size, validate_file_type
from app.config import Config

resumes_bp = Blueprint('resumes', __name__)


@resumes_bp.route('', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload a new resume"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if not data.get('filename') or not data.get('file_base64'):
            return error_response('VALIDATION_ERROR', 'Filename and file data are required', status_code=400)

        filename = data['filename']
        file_base64 = clean_base64(data['file_base64'])

        # Get file extension
        file_type = get_file_extension(filename)
        if not file_type:
            return error_response('INVALID_FILE', 'Unable to determine file type', status_code=400)

        # Validate file type
        is_valid, error = validate_file_type(file_type, Config.ALLOWED_RESUME_EXTENSIONS)
        if not is_valid:
            return error_response('INVALID_FILE_TYPE', error, status_code=400)

        # Validate file size
        file_size = get_file_size_from_base64(file_base64)
        is_valid, error = validate_file_size(file_size, Config.MAX_RESUME_SIZE)
        if not is_valid:
            return error_response('FILE_TOO_LARGE', error, status_code=400)

        # If this is set as default, unset other defaults
        is_default = data.get('is_default', False)
        if is_default:
            Resume.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

        # Create resume
        resume = Resume(
            user_id=user_id,
            filename=filename,
            file_base64=file_base64,
            file_type=file_type,
            file_size=file_size,
            is_default=is_default,
            job_type_tag=data.get('job_type_tag')
        )

        db.session.add(resume)
        db.session.commit()

        return create_response(
            data={'resume': resume.to_dict()},
            message='Resume uploaded successfully',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPLOAD_FAILED', str(e), status_code=500)


@resumes_bp.route('', methods=['GET'])
@jwt_required()
def get_resumes():
    """Get all user resumes"""
    try:
        user_id = get_jwt_identity()
        resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).all()

        return create_response(
            data={
                'resumes': [resume.to_dict() for resume in resumes],
                'count': len(resumes)
            }
        )

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@resumes_bp.route('/<resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """Get a specific resume"""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

        if not resume:
            return error_response('RESUME_NOT_FOUND', 'Resume not found', status_code=404)

        return create_response(data={'resume': resume.to_dict(include_file=False)})

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@resumes_bp.route('/<resume_id>/download', methods=['GET'])
@jwt_required()
def download_resume(resume_id):
    """Download resume (returns base64)"""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

        if not resume:
            return error_response('RESUME_NOT_FOUND', 'Resume not found', status_code=404)

        return create_response(data={'resume': resume.to_dict(include_file=True)})

    except Exception as e:
        return error_response('DOWNLOAD_FAILED', str(e), status_code=500)


@resumes_bp.route('/<resume_id>/default', methods=['PUT'])
@jwt_required()
def set_default_resume(resume_id):
    """Set resume as default"""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

        if not resume:
            return error_response('RESUME_NOT_FOUND', 'Resume not found', status_code=404)

        # Unset other defaults
        Resume.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})

        # Set this as default
        resume.is_default = True
        db.session.commit()

        return create_response(
            data={'resume': resume.to_dict()},
            message='Default resume updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPDATE_FAILED', str(e), status_code=500)


@resumes_bp.route('/<resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """Delete a resume"""
    try:
        user_id = get_jwt_identity()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

        if not resume:
            return error_response('RESUME_NOT_FOUND', 'Resume not found', status_code=404)

        db.session.delete(resume)
        db.session.commit()

        return create_response(message='Resume deleted successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('DELETE_FAILED', str(e), status_code=500)
