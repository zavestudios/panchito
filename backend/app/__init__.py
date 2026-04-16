"""Flask application factory."""
from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from app.auth import auth_bp, init_oauth, login_required_path
from app.config import config_by_name
from app.utils.logging import setup_logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='development'):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name (development, production, testing)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Trust proxy headers for correct URL scheme behind reverse proxy (Cloudflare/Istio)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Load configuration
    app.config.from_object(config_by_name[config_name])
    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")

    # Setup logging
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    init_oauth(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    @app.before_request
    def require_authenticated_session():
        """Protect the app with Keycloak when OIDC is enabled."""
        if not app.config.get("OIDC_ENABLED"):
            return None
        if not login_required_path(request.path):
            return None
        if session.get("user"):
            return None
        return redirect(url_for("auth.login", next=request.url))

    # Log startup
    app.logger.info(f"Panchito Flask app starting in {config_name} mode")

    return app
