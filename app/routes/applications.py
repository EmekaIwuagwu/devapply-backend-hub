from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_, desc, asc, func
from app import db
from app.models.application import Application
from app.utils.auth_utils import create_response, error_response
from app.config import Config

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('', methods=['POST'])
@jwt_required()
def create_application():
    """Create a new job application"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if not data.get('company_name') or not data.get('job_title') or not data.get('platform'):
            return error_response('VALIDATION_ERROR', 'Company name, job title, and platform are required', status_code=400)

        # Create application
        application = Application(
            user_id=user_id,
            company_name=data['company_name'],
            job_title=data['job_title'],
            job_type=data.get('job_type'),
            location=data.get('location'),
            salary_range=data.get('salary_range'),
            status=data.get('status', 'sent'),
            platform=data['platform'],
            job_url=data.get('job_url'),
            resume_used_id=data.get('resume_used_id'),
            cover_letter=data.get('cover_letter'),
            notes=data.get('notes')
        )

        db.session.add(application)
        db.session.commit()

        return create_response(
            data={'application': application.to_dict()},
            message='Application created successfully',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return error_response('CREATE_FAILED', str(e), status_code=500)


@applications_bp.route('', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all applications with filters and pagination"""
    try:
        user_id = get_jwt_identity()

        # Get query parameters
        status_filter = request.args.get('status')
        platform_filter = request.args.get('platform')
        search = request.args.get('search')
        sort = request.args.get('sort', 'most_recent')
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)

        # Build query
        query = Application.query.filter_by(user_id=user_id)

        # Apply filters
        if status_filter:
            query = query.filter_by(status=status_filter)
        if platform_filter:
            query = query.filter_by(platform=platform_filter)
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Application.company_name.ilike(search_term),
                    Application.job_title.ilike(search_term)
                )
            )

        # Apply sorting
        if sort == 'most_recent':
            query = query.order_by(desc(Application.applied_at))
        elif sort == 'oldest':
            query = query.order_by(asc(Application.applied_at))

        # Paginate
        total = query.count()
        applications = query.offset((page - 1) * limit).limit(limit).all()

        return create_response(
            data={
                'applications': [app.to_dict() for app in applications],
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


@applications_bp.route('/<application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get a specific application"""
    try:
        user_id = get_jwt_identity()
        application = Application.query.filter_by(id=application_id, user_id=user_id).first()

        if not application:
            return error_response('APPLICATION_NOT_FOUND', 'Application not found', status_code=404)

        return create_response(data={'application': application.to_dict()})

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@applications_bp.route('/<application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    """Update an application"""
    try:
        user_id = get_jwt_identity()
        application = Application.query.filter_by(id=application_id, user_id=user_id).first()

        if not application:
            return error_response('APPLICATION_NOT_FOUND', 'Application not found', status_code=404)

        data = request.get_json()

        # Update allowed fields
        if 'status' in data:
            application.status = data['status']
            application.last_status_update = datetime.utcnow()
        if 'notes' in data:
            application.notes = data['notes']
        if 'cover_letter' in data:
            application.cover_letter = data['cover_letter']
        if 'job_type' in data:
            application.job_type = data['job_type']
        if 'location' in data:
            application.location = data['location']
        if 'salary_range' in data:
            application.salary_range = data['salary_range']

        db.session.commit()

        return create_response(
            data={'application': application.to_dict()},
            message='Application updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPDATE_FAILED', str(e), status_code=500)


@applications_bp.route('/<application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(application_id):
    """Delete an application"""
    try:
        user_id = get_jwt_identity()
        application = Application.query.filter_by(id=application_id, user_id=user_id).first()

        if not application:
            return error_response('APPLICATION_NOT_FOUND', 'Application not found', status_code=404)

        db.session.delete(application)
        db.session.commit()

        return create_response(message='Application deleted successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('DELETE_FAILED', str(e), status_code=500)


@applications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get application statistics for dashboard"""
    try:
        user_id = get_jwt_identity()

        # Get total applications
        total = Application.query.filter_by(user_id=user_id).count()

        # Get status counts
        status_counts = db.session.query(
            Application.status,
            func.count(Application.id)
        ).filter_by(user_id=user_id).group_by(Application.status).all()

        status_stats = {status: count for status, count in status_counts}

        # Get platform counts
        platform_counts = db.session.query(
            Application.platform,
            func.count(Application.id)
        ).filter_by(user_id=user_id).group_by(Application.platform).all()

        platform_stats = {platform: count for platform, count in platform_counts}

        # Get recent applications
        recent = Application.query.filter_by(user_id=user_id).order_by(
            desc(Application.applied_at)
        ).limit(5).all()

        return create_response(
            data={
                'total_applications': total,
                'status_breakdown': status_stats,
                'platform_breakdown': platform_stats,
                'recent_applications': [app.to_dict() for app in recent]
            }
        )

    except Exception as e:
        return error_response('FETCH_STATS_FAILED', str(e), status_code=500)
