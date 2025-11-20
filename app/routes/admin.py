from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc, or_, func
from datetime import datetime, timedelta
from app import db, limiter
from app.models import (
    User, Application, Payment, Subscription, Video, Settings,
    ActivityLog, AutomationLog
)
from app.utils.auth_utils import generate_tokens, create_response, error_response, admin_required
from app.utils.admin_utils import (
    paginate_query, validate_base64_file, log_admin_activity, get_sort_params
)
from app.utils.email_service import EmailService

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== AUTHENTICATION ENDPOINTS ====================

@admin_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return error_response('MISSING_FIELDS', 'Email and password are required', status_code=400)

    email = data.get('email').lower()
    password = data.get('password')

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return error_response('INVALID_CREDENTIALS', 'Invalid email or password', status_code=401)

    # Check if user has admin role
    if user.role not in ['admin', 'moderator']:
        return error_response('INSUFFICIENT_PERMISSIONS', 'You do not have admin access', status_code=403)

    # Generate tokens
    access_token, refresh_token = generate_tokens(user.id)

    # Log admin login
    log_admin_activity(
        admin_id=user.id,
        action='admin_login',
        entity_type='user',
        entity_id=user.id,
        description=f'Admin {user.email} logged in'
    )

    return create_response(
        data={
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        },
        message='Login successful'
    )


@admin_bp.route('/auth/verify', methods=['GET'])
@admin_required()
def verify_admin_token():
    """Verify admin token and return user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

    return create_response(data={'user': user.to_dict()})


@admin_bp.route('/auth/logout', methods=['POST'])
@admin_required()
def admin_logout():
    """Admin logout endpoint (client should discard tokens)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Log admin logout
    if user:
        log_admin_activity(
            admin_id=user_id,
            action='admin_logout',
            entity_type='user',
            entity_id=user_id,
            description=f'Admin {user.email} logged out'
        )

    return create_response(message='Logout successful')


# ==================== DASHBOARD ENDPOINT ====================

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def get_dashboard():
    """Get admin dashboard statistics and analytics"""
    # Get date range from query params
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total Users
    total_users = User.query.count()
    new_users = User.query.filter(User.created_at >= start_date).count()

    # Total Applications
    total_applications = Application.query.count()
    new_applications = Application.query.filter(Application.applied_at >= start_date).count()

    # Applications by status
    applications_by_status = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()

    # Total Payments and Revenue
    total_payments = Payment.query.filter_by(status='completed').count()
    total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0

    # Recent Payments
    recent_payments = Payment.query.filter(Payment.paid_at >= start_date).filter_by(status='completed')
    new_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.paid_at >= start_date,
        Payment.status == 'completed'
    ).scalar() or 0

    # Active Subscriptions
    active_subscriptions = Subscription.query.filter_by(status='active').count()

    # Recent Activity (last 10 activities)
    recent_activities = ActivityLog.query.order_by(desc(ActivityLog.created_at)).limit(10).all()

    # User Growth (last 7 days)
    user_growth = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = User.query.filter(User.created_at >= day_start, User.created_at < day_end).count()
        user_growth.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': count
        })

    # Application Growth (last 7 days)
    application_growth = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = Application.query.filter(Application.applied_at >= day_start, Application.applied_at < day_end).count()
        application_growth.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': count
        })

    return create_response(data={
        'statistics': {
            'total_users': total_users,
            'new_users': new_users,
            'total_applications': total_applications,
            'new_applications': new_applications,
            'applications_by_status': {status: count for status, count in applications_by_status},
            'total_payments': total_payments,
            'total_revenue': float(total_revenue),
            'new_revenue': float(new_revenue),
            'active_subscriptions': active_subscriptions
        },
        'charts': {
            'user_growth': user_growth,
            'application_growth': application_growth
        },
        'recent_activities': [activity.to_dict() for activity in recent_activities]
    })


# ==================== USER MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/users', methods=['GET'])
@admin_required()
def list_users():
    """List all users with pagination, search, and filters"""
    # Get query parameters
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')  # 'active', 'inactive'
    sort_field, sort_order = get_sort_params(default_sort='created_at', default_order='desc')

    # Build query
    query = User.query

    # Apply search filter
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%')
            )
        )

    # Apply role filter
    if role_filter:
        query = query.filter_by(role=role_filter)

    # Apply status filter
    if status_filter == 'active':
        query = query.filter_by(email_verified=True)
    elif status_filter == 'inactive':
        query = query.filter_by(email_verified=False)

    # Apply sorting
    sort_column = getattr(User, sort_field, User.created_at)
    if sort_order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Paginate
    pagination_data = paginate_query(query)

    return create_response(data={'users': pagination_data})


@admin_bp.route('/users/<user_id>', methods=['GET'])
@admin_required()
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    user = User.query.get(user_id)

    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

    # Get user's applications count
    applications_count = Application.query.filter_by(user_id=user_id).count()

    # Get user's active subscription
    active_subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()

    # Get user's total payments
    total_payments = Payment.query.filter_by(user_id=user_id, status='completed').count()
    total_spent = db.session.query(func.sum(Payment.amount)).filter_by(
        user_id=user_id, status='completed'
    ).scalar() or 0

    # Get recent applications
    recent_applications = Application.query.filter_by(user_id=user_id).order_by(
        desc(Application.applied_at)
    ).limit(5).all()

    return create_response(data={
        'user': user.to_dict(),
        'statistics': {
            'applications_count': applications_count,
            'total_payments': total_payments,
            'total_spent': float(total_spent)
        },
        'active_subscription': active_subscription.to_dict() if active_subscription else None,
        'recent_applications': [app.to_dict() for app in recent_applications]
    })


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required(allowed_roles=['admin'])
def update_user(user_id):
    """Update user role or status"""
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

    data = request.get_json()
    changes = {}

    # Update role if provided
    if 'role' in data:
        old_role = user.role
        new_role = data['role']
        if new_role in ['user', 'admin', 'moderator']:
            user.role = new_role
            changes['role'] = {'from': old_role, 'to': new_role}

    # Update email_verified if provided
    if 'email_verified' in data:
        old_verified = user.email_verified
        new_verified = data['email_verified']
        user.email_verified = new_verified
        changes['email_verified'] = {'from': old_verified, 'to': new_verified}

    db.session.commit()

    # Log activity
    log_admin_activity(
        admin_id=admin_id,
        action='user_updated',
        entity_type='user',
        entity_id=user_id,
        description=f'Updated user {user.email}',
        changes=changes
    )

    return create_response(data={'user': user.to_dict()}, message='User updated successfully')


@admin_bp.route('/users/<user_id>/send-email', methods=['POST'])
@admin_required()
def send_email_to_user(user_id):
    """Send custom email to a specific user"""
    admin_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)

    data = request.get_json()
    subject = data.get('subject')
    message = data.get('message')

    if not subject or not message:
        return error_response('MISSING_FIELDS', 'Subject and message are required', status_code=400)

    # Send email using email service
    try:
        email_service = EmailService()
        email_service.send_email(user.email, subject, message)

        # Log activity
        log_admin_activity(
            admin_id=admin_id,
            action='email_sent',
            entity_type='user',
            entity_id=user_id,
            description=f'Sent email to {user.email}: {subject}'
        )

        return create_response(message='Email sent successfully')
    except Exception as e:
        return error_response('EMAIL_FAILED', f'Failed to send email: {str(e)}', status_code=500)


# ==================== VIDEO MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/videos', methods=['GET'])
@admin_required()
def list_videos():
    """List all videos with pagination"""
    sort_field, sort_order = get_sort_params(default_sort='created_at', default_order='desc')

    # Build query
    query = Video.query

    # Apply sorting
    sort_column = getattr(Video, sort_field, Video.created_at)
    if sort_order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Paginate (without video data to save bandwidth)
    pagination_data = paginate_query(query)

    return create_response(data={'videos': pagination_data})


@admin_bp.route('/videos/<video_id>', methods=['GET'])
@admin_required()
def get_video(video_id):
    """Get a specific video with full data"""
    video = Video.query.get(video_id)

    if not video:
        return error_response('VIDEO_NOT_FOUND', 'Video not found', status_code=404)

    # Increment view count
    video.view_count += 1
    db.session.commit()

    return create_response(data={'video': video.to_dict(include_video=True)})


@admin_bp.route('/videos', methods=['POST'])
@admin_required(allowed_roles=['admin'])
def upload_video():
    """Upload a new video"""
    admin_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    required_fields = ['title', 'video_base64']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return error_response('MISSING_FIELDS', f'Missing required fields: {", ".join(missing)}', status_code=400)

    # Validate video file
    video_validation = validate_base64_file(
        data['video_base64'],
        max_size_mb=50,
        allowed_mime_types=['video/mp4', 'video/webm', 'video/ogg']
    )

    if not video_validation['valid']:
        return error_response('INVALID_VIDEO', video_validation['error'], status_code=400)

    # Validate thumbnail if provided
    if data.get('thumbnail_base64'):
        thumbnail_validation = validate_base64_file(
            data['thumbnail_base64'],
            max_size_mb=5,
            allowed_mime_types=['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        )

        if not thumbnail_validation['valid']:
            return error_response('INVALID_THUMBNAIL', thumbnail_validation['error'], status_code=400)

    # Create video
    video = Video(
        title=data['title'],
        description=data.get('description'),
        video_base64=data['video_base64'],
        thumbnail_base64=data.get('thumbnail_base64'),
        file_size=int(video_validation['size_mb'] * 1024 * 1024),
        duration=data.get('duration'),
        category=data.get('category', 'tutorial'),
        is_active=data.get('is_active', True),
        uploaded_by=admin_id
    )

    db.session.add(video)
    db.session.commit()

    # Log activity
    log_admin_activity(
        admin_id=admin_id,
        action='video_uploaded',
        entity_type='video',
        entity_id=video.id,
        description=f'Uploaded video: {video.title}'
    )

    return create_response(
        data={'video': video.to_dict()},
        message='Video uploaded successfully',
        status_code=201
    )


@admin_bp.route('/videos/<video_id>', methods=['DELETE'])
@admin_required(allowed_roles=['admin'])
def delete_video(video_id):
    """Delete a video"""
    admin_id = get_jwt_identity()
    video = Video.query.get(video_id)

    if not video:
        return error_response('VIDEO_NOT_FOUND', 'Video not found', status_code=404)

    video_title = video.title
    db.session.delete(video)
    db.session.commit()

    # Log activity
    log_admin_activity(
        admin_id=admin_id,
        action='video_deleted',
        entity_type='video',
        entity_id=video_id,
        description=f'Deleted video: {video_title}'
    )

    return create_response(message='Video deleted successfully')


# ==================== PAYMENT MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/payments', methods=['GET'])
@admin_required()
def list_payments():
    """List all payments with pagination, search, and filters"""
    # Get query parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    sort_field, sort_order = get_sort_params(default_sort='paid_at', default_order='desc')

    # Build query
    query = Payment.query

    # Apply search filter (by user email)
    if search:
        query = query.join(User).filter(User.email.ilike(f'%{search}%'))

    # Apply status filter
    if status_filter:
        query = query.filter_by(status=status_filter)

    # Apply sorting
    sort_column = getattr(Payment, sort_field, Payment.paid_at)
    if sort_order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Paginate
    pagination_data = paginate_query(query)

    return create_response(data={'payments': pagination_data})


@admin_bp.route('/payments/<payment_id>', methods=['GET'])
@admin_required()
def get_payment_details(payment_id):
    """Get detailed information about a specific payment"""
    payment = Payment.query.get(payment_id)

    if not payment:
        return error_response('PAYMENT_NOT_FOUND', 'Payment not found', status_code=404)

    # Get user details
    user = User.query.get(payment.user_id)

    # Get subscription details
    subscription = None
    if payment.subscription_id:
        subscription = Subscription.query.get(payment.subscription_id)

    return create_response(data={
        'payment': payment.to_dict(),
        'user': user.to_dict() if user else None,
        'subscription': subscription.to_dict() if subscription else None
    })


# ==================== SETTINGS MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/settings', methods=['GET'])
@admin_required()
def get_settings():
    """Get system settings"""
    settings = Settings.get_settings()
    return create_response(data={'settings': settings.to_dict()})


@admin_bp.route('/settings', methods=['PUT'])
@admin_required(allowed_roles=['admin'])
def update_settings():
    """Update system settings"""
    admin_id = get_jwt_identity()
    settings = Settings.get_settings()
    data = request.get_json()
    changes = {}

    # Update general settings
    if 'general' in data:
        general = data['general']
        for field in ['site_name', 'site_description', 'contact_email', 'support_phone', 'logo_base64']:
            if field in general:
                old_value = getattr(settings, field)
                new_value = general[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    # Update notification settings
    if 'notifications' in data:
        notif = data['notifications']
        for field in ['email_notifications_enabled', 'system_alerts_enabled', 'admin_notification_email', 'low_balance_threshold']:
            if field in notif:
                old_value = getattr(settings, field)
                new_value = notif[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    # Update security settings
    if 'security' in data:
        security = data['security']
        for field in ['session_timeout_minutes', 'max_login_attempts', 'password_min_length', 'require_email_verification', 'two_factor_enabled']:
            if field in security:
                old_value = getattr(settings, field)
                new_value = security[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    # Update system settings
    if 'system' in data:
        system = data['system']
        for field in ['maintenance_mode', 'maintenance_message', 'api_rate_limit_per_hour', 'max_file_upload_mb', 'allowed_file_types']:
            if field in system:
                old_value = getattr(settings, field)
                new_value = system[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    # Update automation settings
    if 'automation' in data:
        automation = data['automation']
        for field in ['max_applications_per_user_per_day', 'auto_cleanup_days']:
            if field in automation:
                old_value = getattr(settings, field)
                new_value = automation[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    # Update feature flags
    if 'features' in data:
        features = data['features']
        for field in ['linkedin_integration_enabled', 'indeed_integration_enabled', 'ai_matching_enabled', 'video_tutorials_enabled']:
            if field in features:
                old_value = getattr(settings, field)
                new_value = features[field]
                setattr(settings, field, new_value)
                if old_value != new_value:
                    changes[field] = {'from': old_value, 'to': new_value}

    settings.updated_by = admin_id
    db.session.commit()

    # Log activity
    log_admin_activity(
        admin_id=admin_id,
        action='settings_updated',
        entity_type='settings',
        entity_id='1',
        description='Updated system settings',
        changes=changes
    )

    return create_response(data={'settings': settings.to_dict()}, message='Settings updated successfully')


@admin_bp.route('/settings/logs', methods=['GET'])
@admin_required()
def get_system_logs():
    """Get system logs (automation logs and activity logs)"""
    log_type = request.args.get('type', 'automation')  # 'automation' or 'activity'

    if log_type == 'automation':
        query = AutomationLog.query.order_by(desc(AutomationLog.created_at))
        pagination_data = paginate_query(query)
        return create_response(data={'logs': pagination_data})
    elif log_type == 'activity':
        query = ActivityLog.query.order_by(desc(ActivityLog.created_at))
        pagination_data = paginate_query(query)
        return create_response(data={'logs': pagination_data})
    else:
        return error_response('INVALID_LOG_TYPE', 'Invalid log type. Use "automation" or "activity"', status_code=400)
