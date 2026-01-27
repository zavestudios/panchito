"""Structured logging configuration."""
import logging
import sys
import structlog


def setup_logging(app):
    """Configure structured logging for the application.

    Args:
        app: Flask application instance
    """
    log_level = app.config.get('LOG_LEVEL', 'INFO')

    # Configure standard library logging
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not app.debug else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set Flask's logger to use structlog
    app.logger = structlog.get_logger('panchito')
