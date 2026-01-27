"""Flask application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

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

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Setup logging
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # Log startup
    app.logger.info(f"Panchito Flask app starting in {config_name} mode")

    return app
