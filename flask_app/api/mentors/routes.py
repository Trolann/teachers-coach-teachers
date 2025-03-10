from flask import Blueprint, request, jsonify
from models.user import User, UserType, ApplicationStatus
from extensions.database import db
from flask_app.extensions.cognito import require_auth, parse_headers, CognitoTokenVerifier
from datetime import datetime

mentor_bp = Blueprint('mentors', __name__, url_prefix='/api/mentors')
verifier = CognitoTokenVerifier()

def get_user_from_token(headers):
    """Helper function to get user from token"""
    auth_token = parse_headers(headers)[0]
    if not auth_token:
        return None
    
    user_info = verifier.get_user_attributes(auth_token)
    if not user_info or 'sub' not in user_info:
        return None
        
    return User.query.filter_by(cognito_sub=user_info['sub']).first()

@mentor_bp.route('/submit_application', methods=['POST'])
@require_auth
def submit_application():
    """Submit a mentor application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Check if user is already a mentor
    if user.user_type == UserType.MENTOR:
        return jsonify({'error': 'Application already exists'}), 409

    # Update user to be a mentor
    user.user_type = UserType.MENTOR
    user.profile = profile_data
    user.application_status = ApplicationStatus.PENDING
    db.session.commit()

    return jsonify({
        'message': 'Application submitted successfully',
        'user_id': user.cognito_sub,
        'status': user.application_status.value
    }), 201

@mentor_bp.route('/update_application', methods=['POST'])
@require_auth
def update_application():
    """Update a mentor application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Check if user is a mentor
    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404

    # Only allow updates if application is pending
    if user.application_status != ApplicationStatus.PENDING:
        return jsonify({'error': 'Cannot update application in current status'}), 403

    # Update profile data
    user.profile.update(profile_data)
    db.session.commit()

    return jsonify({
        'message': 'Application updated successfully',
        'user_id': user.cognito_sub,
        'status': user.application_status.value
    })

@mentor_bp.route('/get_application', methods=['GET'])
@require_auth
def get_application():
    """Get a mentor application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404

    return jsonify({
        'user_id': user.cognito_sub,
        'status': user.application_status.value,
        'submitted_at': user.created_at.isoformat(),
        'profile_data': user.profile
    })

@mentor_bp.route('/get_application_status', methods=['GET'])
@require_auth
def get_application_status():
    """Get the status of a mentor application"""
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    if user.user_type != UserType.MENTOR:
        return jsonify({'error': 'No application found'}), 404

    return jsonify({
        'user_id': user.cognito_sub,
        'status': user.application_status.value,
        'submitted_at': user.created_at.isoformat()
    })
