from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType, ApplicationStatus, db
from flask_app.models.embedding import UserEmbedding
from extensions.logging import get_logger
from faker import Faker
import random
import numpy as np
from uuid import uuid4

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
    mentor_count = User.query.filter_by(user_type=UserType.MENTOR).count()
    logger.info(f'Current mentor count: {mentor_count}')
    
    # Create a simple mapping for the template
    faker_mappings = {field: ['Default'] for field in PROFILE_FIELDS.keys()}
    
    return render_template(
        'dashboard/fake_mentors.html',
        mentor_count=mentor_count,
        profile_fields=list(PROFILE_FIELDS.keys()),
        faker_mappings=faker_mappings
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
            # Generate profile data
            profile_data = {
                field: generator() 
                for field, generator in PROFILE_FIELDS.items()
            }
            
            # Create a user with mentor profile data
            email = fake.unique.email()
            cognito_sub = str(uuid4())  # Generate a fake cognito sub ID
            
            user = User(
                email=email,
                user_type=UserType.MENTOR,
                cognito_sub=cognito_sub,
                profile=profile_data,
                application_status=ApplicationStatus.PENDING
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            logger.debug(f'Created fake mentor user with cognito_sub: {cognito_sub}')

            # Create random vectors for testing (1536 dimensions, normalized)
            # Create multiple embedding types for each user
            embedding_types = ['bio', 'expertise', 'goals']
            
            for embedding_type in embedding_types:
                random_vector = np.random.randn(1536)
                random_vector = random_vector / np.linalg.norm(random_vector)
                
                # Create embedding entry
                embedding = UserEmbedding(
                    user_id=cognito_sub,
                    embedding_type=embedding_type,
                    vector_embedding=random_vector.tolist()
                )
                db.session.add(embedding)
                logger.debug(f'Created fake {embedding_type} embedding for user cognito_sub: {cognito_sub}')
        
        db.session.commit()
        logger.info(f'Successfully generated {num_profiles} fake mentor profiles')
        return jsonify({'success': True, 'count': num_profiles})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error generating fake mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500
