from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import MentorProfile, User, db, MentorStatus
from faker import Faker
import random

fake_mentors_bp = Blueprint('fake_mentors', __name__)
fake = Faker('en_US')

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

@fake_mentors_bp.route('/fake-mentors/generate', methods=['POST'])
def generate_fake_mentors():
    """Generate fake mentor profiles based on form data"""
    try:
        num_profiles = int(request.form.get('numProfiles'))
        if not 1 <= num_profiles <= 100:
            return jsonify({'success': False, 'error': 'Number of profiles must be between 1 and 100'}), 400
        
        for _ in range(num_profiles):
            # Create a user first
            user = User(
                email=fake.unique.email()
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create mentor profile
            mentor = MentorProfile(
                user_id=user.id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(max_nb_chars=200),
                expertise_areas=[fake.job() for _ in range(random.randint(1, 3))],
                years_of_experience=random.randint(1, 20),
                application_status=MentorStatus.PENDING.value  # Use .value to get the string
            )
            db.session.add(mentor)
        
        db.session.commit()
        return jsonify({'success': True, 'count': num_profiles})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
