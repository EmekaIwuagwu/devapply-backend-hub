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
    CORS(app, origins=app.config['CORS_ORIGINS'])

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
