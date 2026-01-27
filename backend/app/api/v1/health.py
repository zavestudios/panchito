"""Health check endpoints."""
from flask import jsonify
from app.api.v1 import api_v1_bp
from app import db


@api_v1_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint.

    Returns:
        JSON response indicating service health
    """
    return jsonify({
        'status': 'healthy',
        'service': 'panchito',
        'version': '1.0.0'
    }), 200


@api_v1_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Readiness check for k8s probes.

    Checks database connectivity.

    Returns:
        JSON response with readiness status
    """
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'ready',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@api_v1_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Liveness check for k8s probes.

    Simple check that the application is running.

    Returns:
        JSON response indicating service is alive
    """
    return jsonify({
        'status': 'alive'
    }), 200
