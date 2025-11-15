from app.routes.auth import auth_bp
from app.routes.resumes import resumes_bp
from app.routes.applications import applications_bp
from app.routes.search_config import search_config_bp
from app.routes.subscription import subscription_bp
from app.routes.platforms import platforms_bp

__all__ = [
    'auth_bp',
    'resumes_bp',
    'applications_bp',
    'search_config_bp',
    'subscription_bp',
    'platforms_bp'
]
