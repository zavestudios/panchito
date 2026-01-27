"""Listings API endpoints."""
from flask import jsonify
from app.api.v1 import api_v1_bp


@api_v1_bp.route('/listings', methods=['GET'])
def get_listings():
    """Get paginated list of real estate listings.

    Returns:
        JSON response with listings data
    """
    # Placeholder - will implement in Phase 2
    return jsonify({
        'data': [],
        'meta': {
            'page': 1,
            'per_page': 50,
            'total': 0
        }
    }), 200


@api_v1_bp.route('/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Get a single listing by ID.

    Args:
        listing_id: The listing identifier

    Returns:
        JSON response with listing data
    """
    # Placeholder - will implement in Phase 2
    return jsonify({
        'data': None,
        'error': 'Not yet implemented'
    }), 404
