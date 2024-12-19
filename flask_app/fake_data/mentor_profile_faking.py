from faker import Faker
from datetime import datetime, timedelta
import random
import numpy as np
from uuid import uuid4

from flask_app.models.user import MentorProfile
from flask_app.extensions.database import db
from flask_app.app import create_app

fake = Faker()

# List of possible expertise areas
EXPERTISE_AREAS = [
    'Python', 'JavaScript', 'React', 'Machine Learning',
    'Data Science', 'DevOps', 'Cloud Architecture',
    'Mobile Development', 'UI/UX Design', 'Product Management'
]


def generate_random_vector():
    """Generate a random 384-dimensional vector for testing"""
    return list(np.random.uniform(-1, 1, 384))


def create_mentor_profile():
    """Create a single mentor profile with fake data"""
    num_expertise = random.randint(2, 5)
    status_choices = ['PENDING', 'APPROVED', 'REJECTED', 'UNDER_REVIEW']

    return {
        'id': str(uuid4()),
        'user_id': str(uuid4()),  # You might want to link to actual users
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'bio': fake.text(max_nb_chars=500),
        'expertise_areas': random.sample(EXPERTISE_AREAS, num_expertise),
        'years_of_experience': random.randint(1, 25),
        'application_status': random.choice(status_choices),
        'application_submitted_at': fake.date_time_between(
            start_date='-1y',
            end_date='now',
            tzinfo=None
        ),
        'vector_embedding': generate_random_vector()
    }


def populate_mentors(num_mentors=10):
    """Populate the database with fake mentor profiles"""
    mentors = []
    for _ in range(num_mentors):
        mentor_data = create_mentor_profile()
        mentor = MentorProfile(**mentor_data)
        mentors.append(mentor)

    # Add all mentors to the database
    db.session.add_all(mentors)
    try:
        db.session.commit()
        print(f"Successfully added {num_mentors} mentor profiles")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding mentor profiles: {e}")
        raise  # Re-raise the exception for debugging