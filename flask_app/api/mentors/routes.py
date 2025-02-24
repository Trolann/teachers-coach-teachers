from flask import Blueprint
from models.user import User
from models.mentor_profiles import MentorProfile, MentorStatus

from flask_app.extensions.cognito import require_auth

mentor_bps = Blueprint('mentors', __name__)

@mentor_bps.route('/submit_application', methods=['POST'])
@require_auth
def submit_application():
    """Submit a mentor application"""
    pass

@mentor_bps.route('/update_application', methods=['POST'])
@require_auth
def update_application():
    """Update a mentor application"""
    pass

@mentor_bps.route('/get_application', methods=['GET'])
@require_auth
def get_application():
    """Get a mentor application"""
    pass

@mentor_bps.route('/get_application_status', methods=['GET'])
@require_auth
def get_application_status():
    """Get the status of a mentor application"""
    pass