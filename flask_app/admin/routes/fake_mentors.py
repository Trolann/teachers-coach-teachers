from flask import Blueprint, render_template, request, jsonify
from models.user import MentorProfile, db
from faker import Faker

fake_mentors_bp = Blueprint('fake_mentors', __name__)
fake = Faker()

FAKER_MAPPINGS = {
    'first_name': ['first_name', 'first_name_male', 'first_name_female'],
    'last_name': ['last_name'],
    'bio': ['text', 'paragraph'],
    'expertise_areas': ['job', 'skill'],
    'years_of_experience': ['random_int']
}

@fake_mentors_bp.route('/fake-mentors')
def fake_mentors_page():
    """Display the fake mentors generation interface"""
    mentor_count = MentorProfile.query.count()
    return render_template(
        'dashboard/fake_mentors.html',
        mentor_count=mentor_count,
        faker_mappings=FAKER_MAPPINGS
    )
