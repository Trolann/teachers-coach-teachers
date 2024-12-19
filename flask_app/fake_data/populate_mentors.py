from faker import Faker
import random
import numpy as np
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ARRAY, Float

# Database connection
DB_URL = "postgresql://postgres:postgres@db:5432/postgres"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Initialize Faker
fake = Faker()

# Model definition
class MentorProfile(Base):
    __tablename__ = 'mentor_profile'
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    bio = Column(String)
    expertise_areas = Column(ARRAY(String))
    years_of_experience = Column(Integer)
    application_status = Column(String)
    application_submitted_at = Column(DateTime)
    vector_embedding = Column(ARRAY(Float))

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

    return MentorProfile(
        id=str(uuid4()),
        user_id=str(uuid4()),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        bio=fake.text(max_nb_chars=500),
        expertise_areas=random.sample(EXPERTISE_AREAS, num_expertise),
        years_of_experience=random.randint(1, 25),
        application_status=random.choice(status_choices),
        application_submitted_at=fake.date_time_between(
            start_date='-1y',
            end_date='now',
            tzinfo=None
        ),
        vector_embedding=generate_random_vector()
    )

def populate_mentors(num_mentors=10):
    """Populate the database with fake mentor profiles"""
    session = Session()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        # Create and add mentor profiles
        mentors = [create_mentor_profile() for _ in range(num_mentors)]
        session.add_all(mentors)
        session.commit()
        print(f"Successfully added {num_mentors} mentor profiles")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding mentor profiles: {e}")
        return False
    finally:
        session.close()

if __name__ == '__main__':
    populate_mentors(10)
