import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow

from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)

    # Configure CORS with comprehensive settings for frontend integration
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         expose_headers=['Content-Type', 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    )

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'DevApply Backend'
            }
        }), 200

    # System status endpoint - shows if all services are running
    @app.route('/api/system/status', methods=['GET'])
    def system_status():
        """
        Check status of all system components:
        - Web API (always true if this responds)
        - Database connection
        - Redis connection
        - Celery worker
        - Celery beat scheduler
        """
        import os
        from datetime import datetime

        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'services': {},
            'overall_status': 'healthy'
        }

        # Web API (always true if we get here)
        status['services']['web_api'] = {
            'status': 'running',
            'message': 'Web API is responding'
        }

        # Check Database
        try:
            db.session.execute('SELECT 1')
            status['services']['database'] = {
                'status': 'connected',
                'message': 'Database connection successful'
            }
        except Exception as e:
            status['services']['database'] = {
                'status': 'error',
                'message': f'Database connection failed: {str(e)}'
            }
            status['overall_status'] = 'degraded'

        # Check Redis
        try:
            import redis
            redis_url = os.getenv('REDIS_URL') or os.getenv('CELERY_BROKER_URL')
            if redis_url:
                r = redis.from_url(redis_url)
                r.ping()
                status['services']['redis'] = {
                    'status': 'connected',
                    'message': 'Redis connection successful'
                }
            else:
                status['services']['redis'] = {
                    'status': 'not_configured',
                    'message': 'Redis URL not configured'
                }
        except Exception as e:
            status['services']['redis'] = {
                'status': 'error',
                'message': f'Redis connection failed: {str(e)}'
            }
            status['overall_status'] = 'degraded'

        # Check Celery Worker
        try:
            from app.celery_config import celery
            inspect = celery.control.inspect(timeout=2.0)
            active_workers = inspect.active()

            if active_workers and len(active_workers) > 0:
                worker_count = len(active_workers)
                status['services']['celery_worker'] = {
                    'status': 'running',
                    'message': f'{worker_count} worker(s) active',
                    'workers': list(active_workers.keys())
                }
            else:
                status['services']['celery_worker'] = {
                    'status': 'not_running',
                    'message': '⚠️ NO CELERY WORKERS DETECTED - Background processing will not work!',
                    'action_required': 'Deploy devapply-worker service in Render'
                }
                status['overall_status'] = 'critical'
        except Exception as e:
            status['services']['celery_worker'] = {
                'status': 'error',
                'message': f'Cannot check Celery workers: {str(e)}'
            }
            status['overall_status'] = 'degraded'

        # Check Celery Beat
        try:
            from app.celery_config import celery
            inspect = celery.control.inspect(timeout=2.0)
            scheduled = inspect.scheduled()

            if scheduled and len(scheduled) > 0:
                status['services']['celery_beat'] = {
                    'status': 'running',
                    'message': 'Celery beat scheduler is active'
                }
            else:
                status['services']['celery_beat'] = {
                    'status': 'not_running',
                    'message': '⚠️ NO CELERY BEAT SCHEDULER DETECTED - Scheduled tasks will not run!',
                    'action_required': 'Deploy devapply-beat service in Render'
                }
                status['overall_status'] = 'critical'
        except Exception as e:
            status['services']['celery_beat'] = {
                'status': 'unknown',
                'message': f'Cannot check Celery beat: {str(e)}'
            }

        # Add recommendations
        if status['overall_status'] == 'critical':
            status['recommendations'] = [
                'Check Render dashboard for devapply-worker service',
                'Check Render dashboard for devapply-beat service',
                'Ensure worker services are deployed and running',
                'View TROUBLESHOOTING.md in the repository for detailed instructions'
            ]

        return jsonify({
            'success': True,
            'data': status
        }), 200

    return app


def register_blueprints(app):
    """Register application blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.resumes import resumes_bp
    from app.routes.applications import applications_bp
    from app.routes.search_config import search_config_bp
    from app.routes.subscription import subscription_bp
    from app.routes.platforms import platforms_bp
    from app.routes.automation import automation_bp
    from app.routes.credentials import credentials_bp
    from app.routes.preferences import preferences_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resumes_bp, url_prefix='/api/resumes')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(search_config_bp, url_prefix='/api/search-config')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
    app.register_blueprint(platforms_bp, url_prefix='/api/platforms')
    app.register_blueprint(automation_bp, url_prefix='/api/automation')
    app.register_blueprint(credentials_bp, url_prefix='/api/credentials')
    app.register_blueprint(preferences_bp, url_prefix='/api/preferences')
    app.register_blueprint(admin_bp)  # Already has /api/admin prefix in blueprint definition


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(error),
                'details': {}
            }
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required',
                'details': {}
            }
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Access denied',
                'details': {}
            }
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found',
                'details': {}
            }
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An internal error occurred',
                'details': {}
            }
        }), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Too many requests. Please try again later.',
                'details': {}
            }
        }), 429
