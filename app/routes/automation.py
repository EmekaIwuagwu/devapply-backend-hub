from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func
from app import db
from app.models.job_queue import JobQueue
from app.models.automation_log import AutomationLog
from app.models.job_listing import JobListing
from app.utils.auth_utils import create_response, error_response
from app.utils.rate_limiter import ApplicationRateLimiter
from app.config import Config

automation_bp = Blueprint('automation', __name__)


@automation_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_job_queue():
    """Get pending jobs in queue for user"""
    try:
        user_id = get_jwt_identity()

        # Get query parameters
        status = request.args.get('status', 'pending')
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)

        # Build query
        query = JobQueue.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        # Order by priority and created date
        query = query.order_by(
            desc(JobQueue.priority),
            JobQueue.created_at.asc()
        )

        # Paginate
        total = query.count()
        jobs = query.offset((page - 1) * limit).limit(limit).all()

        return create_response(
            data={
                'jobs': [job.to_dict() for job in jobs],
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


@automation_bp.route('/queue/<job_id>/skip', methods=['POST'])
@jwt_required()
def skip_job(job_id):
    """Skip a job in the queue"""
    try:
        user_id = get_jwt_identity()
        job = JobQueue.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            return error_response('JOB_NOT_FOUND', 'Job not found', status_code=404)

        if job.status != 'pending':
            return error_response('INVALID_STATUS', f'Cannot skip job with status: {job.status}', status_code=400)

        job.status = 'skipped'
        db.session.commit()

        return create_response(
            data={'job': job.to_dict()},
            message='Job skipped successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('SKIP_FAILED', str(e), status_code=500)


@automation_bp.route('/queue/<job_id>/priority', methods=['PUT'])
@jwt_required()
def update_job_priority(job_id):
    """Update job priority"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        priority = data.get('priority')
        if priority is None or not (1 <= priority <= 10):
            return error_response('INVALID_PRIORITY', 'Priority must be between 1 and 10', status_code=400)

        job = JobQueue.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            return error_response('JOB_NOT_FOUND', 'Job not found', status_code=404)

        job.priority = priority
        db.session.commit()

        return create_response(
            data={'job': job.to_dict()},
            message='Priority updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return error_response('UPDATE_FAILED', str(e), status_code=500)


@automation_bp.route('/queue/<job_id>', methods=['DELETE'])
@jwt_required()
def remove_from_queue(job_id):
    """Remove job from queue"""
    try:
        user_id = get_jwt_identity()
        job = JobQueue.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            return error_response('JOB_NOT_FOUND', 'Job not found', status_code=404)

        db.session.delete(job)
        db.session.commit()

        return create_response(message='Job removed from queue successfully')

    except Exception as e:
        db.session.rollback()
        return error_response('DELETE_FAILED', str(e), status_code=500)


@automation_bp.route('/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get automation status and statistics"""
    try:
        user_id = get_jwt_identity()

        # Get queue statistics
        pending_count = JobQueue.query.filter_by(user_id=user_id, status='pending').count()
        processing_count = JobQueue.query.filter_by(user_id=user_id, status='processing').count()
        applied_count = JobQueue.query.filter_by(user_id=user_id, status='applied').count()
        failed_count = JobQueue.query.filter_by(user_id=user_id, status='failed').count()

        # Get rate limit status
        rate_stats = ApplicationRateLimiter.get_user_stats(user_id)

        # Get next scheduled job
        next_job = JobQueue.query.filter_by(
            user_id=user_id,
            status='pending'
        ).order_by(JobQueue.scheduled_for.asc()).first()

        return create_response(
            data={
                'queue_stats': {
                    'pending': pending_count,
                    'processing': processing_count,
                    'applied': applied_count,
                    'failed': failed_count
                },
                'rate_limits': rate_stats,
                'next_scheduled_job': next_job.to_dict() if next_job else None,
                'is_active': pending_count > 0 or processing_count > 0
            }
        )

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)


@automation_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_automation_logs():
    """Get automation activity logs"""
    try:
        user_id = get_jwt_identity()

        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)
        action_type = request.args.get('action_type')
        status = request.args.get('status')

        query = AutomationLog.query.filter_by(user_id=user_id)

        if action_type:
            query = query.filter_by(action_type=action_type)
        if status:
            query = query.filter_by(status=status)

        query = query.order_by(desc(AutomationLog.created_at))

        total = query.count()
        logs = query.offset((page - 1) * limit).limit(limit).all()

        return create_response(
            data={
                'logs': [log.to_dict() for log in logs],
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


@automation_bp.route('/discovered-jobs', methods=['GET'])
@jwt_required()
def get_discovered_jobs():
    """Get recently discovered jobs matching user criteria"""
    try:
        user_id = get_jwt_identity()

        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)
        platform = request.args.get('platform')

        # Get jobs that were found but not yet queued
        query = JobListing.query.filter_by(is_active=True)

        if platform:
            query = query.filter_by(platform=platform)

        # Exclude jobs already in queue for this user
        queued_job_ids = db.session.query(JobQueue.job_listing_id).filter_by(user_id=user_id).subquery()
        query = query.filter(~JobListing.id.in_(queued_job_ids))

        query = query.order_by(desc(JobListing.scraped_at))

        total = query.count()
        jobs = query.offset((page - 1) * limit).limit(limit).all()

        return create_response(
            data={
                'jobs': [job.to_dict() for job in jobs],
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


@automation_bp.route('/discovered-jobs/<job_id>/queue', methods=['POST'])
@jwt_required()
def queue_discovered_job(job_id):
    """Manually add a discovered job to the queue"""
    try:
        user_id = get_jwt_identity()
        from datetime import datetime

        job_listing = JobListing.query.get(job_id)
        if not job_listing:
            return error_response('JOB_NOT_FOUND', 'Job listing not found', status_code=404)

        # Check if already queued
        existing = JobQueue.query.filter_by(
            user_id=user_id,
            job_listing_id=job_id
        ).first()

        if existing:
            return error_response('ALREADY_QUEUED', 'Job already in queue', status_code=400)

        # Get user's active search config
        from app.models.job_search_config import JobSearchConfig
        config = JobSearchConfig.query.filter_by(user_id=user_id, is_active=True).first()

        # Add to queue
        queue_item = JobQueue(
            user_id=user_id,
            job_search_config_id=config.id if config else None,
            platform=job_listing.platform,
            job_listing_id=job_listing.id,
            company_name=job_listing.company_name,
            job_title=job_listing.job_title,
            job_url=job_listing.job_url,
            status='pending',
            priority=5,  # Default priority
            match_score=0,
            scheduled_for=datetime.utcnow()
        )

        db.session.add(queue_item)
        db.session.commit()

        return create_response(
            data={'queue_item': queue_item.to_dict()},
            message='Job added to queue successfully',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return error_response('QUEUE_FAILED', str(e), status_code=500)
