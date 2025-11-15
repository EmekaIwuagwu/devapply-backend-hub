from flask import Blueprint
from app.models.platform import Platform
from app.utils.auth_utils import create_response, error_response

platforms_bp = Blueprint('platforms', __name__)


@platforms_bp.route('', methods=['GET'])
def get_platforms():
    """Get all available platforms"""
    try:
        platforms = Platform.query.filter_by(is_enabled=True).all()

        # Separate popular and other platforms
        popular = [p.to_dict() for p in platforms if p.is_popular]
        others = [p.to_dict() for p in platforms if not p.is_popular]

        return create_response(
            data={
                'popular': popular,
                'others': others,
                'all': [p.to_dict() for p in platforms]
            }
        )

    except Exception as e:
        return error_response('FETCH_FAILED', str(e), status_code=500)
