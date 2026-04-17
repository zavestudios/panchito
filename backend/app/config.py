"""Application configuration."""
import os
from pathlib import Path


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Get database credentials
    DB_USER = os.getenv('DB_USER', 'root')
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_NAME = os.getenv('DB_NAME', 'example')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # Read password from Docker secret or env var
    DB_PASSWORD_FILE = os.getenv('DB_PASSWORD_FILE', '/run/secrets/db-password')
    if Path(DB_PASSWORD_FILE).exists():
        with open(DB_PASSWORD_FILE, 'r') as f:
            DB_PASSWORD = f.read().strip()
    else:
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )

    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True

    # API Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100

    # Data ingestion
    DATA_DIR = Path('/app/data/datasets')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # OIDC / Keycloak
    OIDC_ENABLED = os.getenv('OIDC_ENABLED', 'false').lower() in {'1', 'true', 'yes', 'on'}
    OIDC_ISSUER_URL = os.getenv('OIDC_ISSUER_URL')
    OIDC_CLIENT_ID = os.getenv('OIDC_CLIENT_ID')
    OIDC_CLIENT_SECRET = os.getenv('OIDC_CLIENT_SECRET')
    OIDC_SCOPES = os.getenv('OIDC_SCOPES', 'openid profile email')
    APP_BASE_URL = os.getenv('APP_BASE_URL')

    # Session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in {'1', 'true', 'yes', 'on'}


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    # Require secret key in production
    SECRET_KEY = os.getenv('SECRET_KEY')


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously in tests
    CELERY_TASK_EAGER_PROPAGATES = True


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
