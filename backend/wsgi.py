"""WSGI application entrypoint."""
import os
from app import create_app

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create application instance
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
