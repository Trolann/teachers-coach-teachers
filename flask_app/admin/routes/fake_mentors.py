from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, db
from flask_app.models.mentor_profiles import MentorProfile, MentorStatus
from flask_app.models.vector import MentorVector
from extensions.logging import get_logger
from faker import Faker
import random
import numpy as np

logger = get_logger(__name__)
fake_mentors_bp = Blueprint('fake_mentors', __name__)
fake = Faker('en_US')

PROFILE_FIELDS = {
    'first_name': lambda: fake.first_name(),
    'last_name': lambda: fake.last_name(),
    'bio': lambda: fake.text(max_nb_chars=200),
    'expertise_areas': lambda: [fake.job() for _ in range(random.randint(1, 3))],
    'years_of_experience': lambda: random.randint(1, 20)
}

@fake_mentors_bp.route('/fake-mentors')
def fake_mentors_page():
    """Display the fake mentors generation interface"""
    logger.debug('Accessing fake mentors generation page')
    mentor_count = MentorProfile.query.count()
    logger.info(f'Current mentor count: {mentor_count}')
    return render_template(
        'dashboard/fake_mentors.html',
        mentor_count=mentor_count,
        profile_fields=list(PROFILE_FIELDS.keys())
    )

@fake_mentors_bp.route('/fake-mentors/generate', methods=['POST'])
def generate_fake_mentors():
    """Generate fake mentor profiles based on form data"""
    logger.debug(f'Received request to generate fake mentors. Form data: {request.form}')
    try:
        num_profiles = int(request.form.get('numProfiles'))
        logger.info(f'Attempting to generate {num_profiles} fake mentor profiles')
        
        if not 1 <= num_profiles <= 100:
            logger.warning(f'Invalid number of profiles requested: {num_profiles}')
            return jsonify({'success': False, 'error': 'Number of profiles must be between 1 and 100'}), 400
        
        for _ in range(num_profiles):
            # Create a user first
            email = fake.unique.email()
            user = User(email=email)
            db.session.add(user)
            db.session.flush()  # Get the user ID
            logger.debug(f'Created fake user with ID: {user.id}')
            
            # Generate profile data
            profile_data = {
                field: generator() 
                for field, generator in PROFILE_FIELDS.items()
            }
            
            # Create mentor profile
            mentor = MentorProfile(
                user_id=user.id,
                profile_data=profile_data,
                application_status=MentorStatus.PENDING.value
            )
            db.session.add(mentor)
            logger.debug(f'Created fake mentor profile for user ID: {user.id}')

            # Create a random vector for testing (1536 dimensions, normalized)
            random_vector = np.random.randn(1536)
            random_vector = random_vector / np.linalg.norm(random_vector)
            
            # Create vector entry
            vector = MentorVector(
                user_id=user.id,
                embedding=random_vector.tolist()
            )
            db.session.add(vector)
            logger.debug(f'Created fake vector for user ID: {user.id}')
        
        db.session.commit()
        logger.info(f'Successfully generated {num_profiles} fake mentor profiles')
        return jsonify({'success': True, 'count': num_profiles})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error generating fake mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500
