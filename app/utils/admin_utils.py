import base64
import re
from flask import request


def paginate_query(query, page=None, per_page=None):
    """
    Paginate a SQLAlchemy query and return formatted results.

    Args:
        query: SQLAlchemy query object
        page: Page number (default: from request args or 1)
        per_page: Items per page (default: from request args or 20)

    Returns:
        dict: Pagination data including items, total, pages, etc.
    """
    # Get pagination params from request or use defaults
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = request.args.get('per_page', 20, type=int)

    # Validate pagination params
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Max 100 items per page

    # Execute pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_page': pagination.next_num if pagination.has_next else None,
        'prev_page': pagination.prev_num if pagination.has_prev else None
    }


def validate_base64_file(base64_string, max_size_mb=50, allowed_mime_types=None):
    """
    Validate a base64 encoded file.

    Args:
        base64_string: Base64 encoded file string (with or without data URI prefix)
        max_size_mb: Maximum file size in megabytes
        allowed_mime_types: List of allowed MIME types (e.g., ['video/mp4', 'image/jpeg'])

    Returns:
        dict: {'valid': bool, 'error': str or None, 'mime_type': str, 'size_mb': float}
    """
    if not base64_string:
        return {'valid': False, 'error': 'No file data provided', 'mime_type': None, 'size_mb': 0}

    # Extract MIME type and base64 data from data URI if present
    mime_type = None
    if base64_string.startswith('data:'):
        try:
            # Format: data:mime/type;base64,actualdata
            match = re.match(r'data:([^;]+);base64,(.+)', base64_string)
            if match:
                mime_type = match.group(1)
                base64_data = match.group(2)
            else:
                return {'valid': False, 'error': 'Invalid data URI format', 'mime_type': None, 'size_mb': 0}
        except Exception as e:
            return {'valid': False, 'error': f'Failed to parse data URI: {str(e)}', 'mime_type': None, 'size_mb': 0}
    else:
        base64_data = base64_string

    # Validate base64 format
    try:
        decoded = base64.b64decode(base64_data, validate=True)
    except Exception as e:
        return {'valid': False, 'error': f'Invalid base64 encoding: {str(e)}', 'mime_type': mime_type, 'size_mb': 0}

    # Calculate file size
    size_bytes = len(decoded)
    size_mb = size_bytes / (1024 * 1024)

    # Check file size
    if size_mb > max_size_mb:
        return {
            'valid': False,
            'error': f'File size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)',
            'mime_type': mime_type,
            'size_mb': size_mb
        }

    # Check MIME type if specified
    if allowed_mime_types and mime_type:
        if mime_type not in allowed_mime_types:
            return {
                'valid': False,
                'error': f'File type ({mime_type}) not allowed. Allowed types: {", ".join(allowed_mime_types)}',
                'mime_type': mime_type,
                'size_mb': size_mb
            }

    return {
        'valid': True,
        'error': None,
        'mime_type': mime_type,
        'size_mb': round(size_mb, 2)
    }


def log_admin_activity(admin_id, action, entity_type, entity_id, description, changes=None, status='success'):
    """
    Log an admin activity to the database.

    Args:
        admin_id: ID of the admin user
        action: Action performed (e.g., 'user_updated', 'video_uploaded')
        entity_type: Type of entity affected (e.g., 'user', 'video')
        entity_id: ID of the affected entity
        description: Human-readable description
        changes: Dict of changes made (before/after)
        status: Status of the action ('success', 'failed', 'warning')
    """
    from app.models import ActivityLog
    from app import db

    try:
        # Get IP address and user agent from request context
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')[:500]

        activity = ActivityLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes or {},
            status=status
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Failed to log admin activity: {str(e)}")


def get_sort_params(default_sort='created_at', default_order='desc'):
    """
    Get sorting parameters from request args.

    Args:
        default_sort: Default field to sort by
        default_order: Default sort order ('asc' or 'desc')

    Returns:
        tuple: (sort_field, sort_order)
    """
    sort_field = request.args.get('sort', default_sort)
    sort_order = request.args.get('order', default_order).lower()

    # Validate sort order
    if sort_order not in ['asc', 'desc']:
        sort_order = default_order

    return sort_field, sort_order
