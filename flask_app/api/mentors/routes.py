from flask import Blueprint, request, jsonify
from models.user import User
from models.mentor_profiles import MentorProfile, MentorStatus
from extensions.database import db
from flask_app.extensions.cognito import require_auth, parse_headers, CognitoTokenVerifier

mentor_bp = Blueprint('mentors', __name__)
verifier = CognitoTokenVerifier()

@mentor_bp.route('/submit_application', methods=['POST'])
@require_auth
def submit_application():
    """Submit a mentor application"""
    auth_token, _, _, _ = parse_headers(request.headers)
    user = verifier.get_user_attributes(auth_token)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Check if user already has a profile
    existing_profile = MentorProfile.query.filter_by(user_id=user.id).first()
    if existing_profile:
        return jsonify({'error': 'Application already exists'}), 409

    # Create new profile
    profile = MentorProfile(user_id=user.id, profile_data=profile_data)
    db.session.add(profile)
    db.session.commit()

    return jsonify({
        'message': 'Application submitted successfully',
        'profile_id': profile.id,
        'status': profile.application_status
    }), 201

@mentor_bp.route('/update_application', methods=['POST'])
@require_auth
def update_application():
    """Update a mentor application"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get JSON data from request
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({'error': 'No profile data provided'}), 400

    # Get existing profile
    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({'error': 'No application found'}), 404

    # Only allow updates if application is pending
    if profile.application_status != MentorStatus.PENDING.value:
        return jsonify({'error': 'Cannot update application in current status'}), 403

    # Update profile data
    profile.profile_data.update(profile_data)
    db.session.commit()

    return jsonify({
        'message': 'Application updated successfully',
        'profile_id': profile.id,
        'status': profile.application_status
    })

@mentor_bp.route('/get_application', methods=['GET'])
@require_auth
def get_application():
    """Get a mentor application"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({'error': 'No application found'}), 404

    return jsonify({
        'profile_id': profile.id,
        'status': profile.application_status,
        'submitted_at': profile.application_submitted_at.isoformat(),
        'profile_data': profile.profile_data
    })

@mentor_bp.route('/get_application_status', methods=['GET'])
@require_auth
def get_application_status():
    """Get the status of a mentor application"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({'error': 'No application found'}), 404

    return jsonify({
        'profile_id': profile.id,
        'status': profile.application_status,
        'submitted_at': profile.application_submitted_at.isoformat()
    })
