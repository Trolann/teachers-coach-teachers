from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType, ApplicationStatus
from flask_app.models.embedding import UserEmbedding
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.logging import get_logger
from extensions.database import db
import json
from uuid import uuid4

logger = get_logger(__name__)
fake_mentors_bp = Blueprint('fake_mentors', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()


@fake_mentors_bp.route('/fake-mentors')
def fake_mentors_page():
    """Display the mentor import and matching test interface"""
    logger.debug('Accessing mentor import and matching test page')
    mentor_count = User.query.filter_by(user_type=UserType.MENTOR).count()
    logger.info(f'Current mentor count: {mentor_count}')

    return render_template(
        'dashboard/fake_mentors.html',
        mentor_count=mentor_count
    )


@fake_mentors_bp.route('/fake-mentors/import', methods=['POST'])
def import_mentors_from_json():
    """Import mentor profiles from a JSON/JSONL file"""
    logger.debug('Received request to import mentors from JSON')
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Get the number of profiles to import
        num_profiles = int(request.form.get('numProfiles', 0))
        if num_profiles <= 0:
            return jsonify({'success': False, 'error': 'Number of profiles must be greater than 0'}), 400

        # Read and parse the file
        file_content = file.read().decode('utf-8')

        # Try to parse as JSONL (line-delimited JSON)
        try:
            profiles = []
            for line in file_content.strip().split('\n'):
                if line.strip():  # Skip empty lines
                    profiles.append(json.loads(line))
        except json.JSONDecodeError:
            # If JSONL parsing fails, try as regular JSON
            try:
                profiles = json.loads(file_content)
                # Handle the case where the JSON is a dict instead of a list
                if isinstance(profiles, dict):
                    profiles = [profiles]
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid JSON/JSONL format'}), 400

        logger.info(f'Found {len(profiles)} profiles in the file')

        # Check if we have enough profiles
        if num_profiles > len(profiles):
            return jsonify({
                'success': False,
                'error': f'Requested {num_profiles} profiles but only {len(profiles)} available in file'
            }), 400

        # Limit the number of profiles to import
        profiles = profiles[:num_profiles]

        # Import each profile
        imported_count = 0
        for profile in profiles:
            try:
                # Validate the profile has required fields
                if not all(key in profile for key in ['first_name', 'last_name', 'email']):
                    logger.warning(f'Skipping profile missing required fields: {profile}')
                    continue

                # Create a user with mentor profile data
                email = profile.get('email')
                cognito_sub = str(uuid4())  # Generate a fake cognito sub ID

                # Check if a user with this email already exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    logger.warning(f'User with email {email} already exists, skipping')
                    continue

                user = User(
                    email=email,
                    user_type="MENTOR",
                    cognito_sub=cognito_sub,
                    profile=profile,
                    application_status="APPROVED"  # Set as approved to ensure they appear in matching
                )
                db.session.add(user)
                db.session.flush()  # Get the user ID
                logger.debug(f'Created imported mentor user with cognito_sub: {cognito_sub}')

                # Prepare embedding data from profile
                embedding_data = {}

                # Add bio if available
                if 'bio' in profile:
                    embedding_data['bio'] = profile['bio']

                # Add expertise if available
                if 'expertise_areas' in profile:
                    if isinstance(profile['expertise_areas'], list):
                        embedding_data['expertise'] = ', '.join(profile['expertise_areas'])
                    else:
                        embedding_data['expertise'] = str(profile['expertise_areas'])

                # Add experience if available
                if 'years_of_experience' in profile:
                    embedding_data['experience'] = f"{profile['years_of_experience']} years of experience"

                # Add skills if available
                if 'skills' in profile:
                    if isinstance(profile['skills'], list):
                        embedding_data['skills'] = ', '.join(profile['skills'])
                    else:
                        embedding_data['skills'] = str(profile['skills'])

                # Add any other relevant fields
                for key, value in profile.items():
                    if key not in embedding_data and isinstance(value, (str, int, float)):
                        embedding_data[key] = str(value)

                # Generate real embeddings
                if embedding_data:
                    try:
                        embedding_factory.store_embedding(cognito_sub, embedding_data)
                        logger.debug(f'Created embeddings for user {cognito_sub}')
                    except Exception as e:
                        logger.error(f'Error creating embeddings for user {cognito_sub}: {str(e)}')

                imported_count += 1
            except Exception as e:
                logger.error(f'Error importing profile: {str(e)}')
                logger.exception(e)

        db.session.commit()
        logger.info(f'Successfully imported {imported_count} mentor profiles')
        return jsonify({'success': True, 'count': imported_count})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error importing mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/generate', methods=['POST'])
def generate_fake_mentors():
    """Generate fake mentor profiles one at a time"""
    global generation_progress
    logger.debug('Received request to generate fake mentors')
    
    # Check if generation is already in progress
    if generation_progress['in_progress']:
        return jsonify({
            'success': False, 
            'error': 'Generation already in progress'
        }), 409
    
    try:
        # Get the number of profiles to generate
        num_profiles = int(request.form.get('numProfiles', 0))
        if num_profiles <= 0:
            return jsonify({'success': False, 'error': 'Number of profiles must be greater than 0'}), 400
        
        if num_profiles > 100:
            return jsonify({'success': False, 'error': 'Maximum 100 profiles can be generated at once'}), 400

        logger.info(f'Generating {num_profiles} fake mentor profiles')
        
        # Reset progress tracking
        generation_progress['total'] = num_profiles
        generation_progress['current'] = 0
        generation_progress['in_progress'] = True
        generation_progress['error'] = None
        
        # Generate the first profile and return success
        # The client will poll for progress and the remaining profiles will be generated
        _generate_next_profile()
        
        return jsonify({
            'success': True, 
            'message': 'Profile generation started',
            'total': num_profiles
        })
    except Exception as e:
        generation_progress['in_progress'] = False
        generation_progress['error'] = str(e)
        logger.error(f'Error starting fake mentor generation: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


def _generate_next_profile():
    """Generate the next profile in the queue"""
    global generation_progress
    
    try:
        if not generation_progress['in_progress']:
            return
            
        if generation_progress['current'] >= generation_progress['total']:
            # All profiles generated
            generation_progress['in_progress'] = False
            logger.info(f'Successfully generated {generation_progress["current"]} fake mentor profiles')
            return
            
        # Generate a unique email
        i = generation_progress['current']
        email = f"mentor{uuid4().hex[:8]}@example.com"
        
        # Generate a fake cognito sub ID
        cognito_sub = str(uuid4())
        
        # Create a basic profile
        profile = {
            "first_name": f"Mentor{i+1}",
            "last_name": f"Test{i+1}",
            "email": email,
            "bio": f"I am a test mentor {i+1} with expertise in various areas.",
            "expertise_areas": ["Software Development", "Data Science", "Product Management"],
            "years_of_experience": 5 + (i % 15),  # 5-20 years of experience
            "skills": ["Python", "JavaScript", "Leadership", "Communication"]
        }
        
        # Create the user
        user = User(
            email=email,
            user_type="MENTOR",
            cognito_sub=cognito_sub,
            profile=profile,
            application_status="APPROVED"  # Set as approved to ensure they appear in matching
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Prepare embedding data
        embedding_data = {
            "bio": profile["bio"],
            "expertise": ", ".join(profile["expertise_areas"]),
            "experience": f"{profile['years_of_experience']} years of experience",
            "skills": ", ".join(profile["skills"])
        }
        
        # Generate embeddings
        embedding_factory.store_embedding(cognito_sub, embedding_data)
        
        # Commit the transaction for this profile
        db.session.commit()
        
        # Update progress
        generation_progress['current'] += 1
        logger.debug(f'Generated fake mentor {generation_progress["current"]}/{generation_progress["total"]}')
        
        # Generate the next profile
        _generate_next_profile()
    except Exception as e:
        db.session.rollback()
        generation_progress['error'] = str(e)
        generation_progress['in_progress'] = False
        logger.error(f'Error generating mentor: {str(e)}')
        logger.exception(e)


@fake_mentors_bp.route('/fake-mentors/test-matching', methods=['POST'])
def test_matching():
    """Test the matching algorithm with a query"""
    logger.debug('Received request to test matching')
    try:
        # Get the user_id to test as
        user_id = request.form.get('user_id')
        if not user_id:
            user_id = str(uuid4())  # Generate a temporary user ID for testing
            logger.info(f'No user_id provided, using generated ID: {user_id}')
        
        # Get the search criteria from the form
        search_json = request.form.get('search_criteria', '{}')
        try:
            criteria = json.loads(search_json)
            if not isinstance(criteria, dict):
                return jsonify({'success': False, 'error': 'Search criteria must be a valid JSON object'}), 400
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON in search criteria: {str(e)}')
            return jsonify({'success': False, 'error': f'Invalid JSON format: {str(e)}'}), 400

        # Get the limit parameter
        try:
            limit = int(request.form.get('limit', 10))
        except ValueError:
            limit = 10

        logger.info(f'Testing matching with user_id: {user_id}, criteria: {criteria}, limit: {limit}')
        
        # Use the algorithm to find matches
        matches = the_algorithm.get_closest_embeddings(user_id, criteria, limit)

        # Format the response
        formatted_matches = []
        for match in matches:
            user = User.query.filter_by(cognito_sub=match["user_id"]).first()
            if user:
                formatted_matches.append({
                    "user_id": match["user_id"],
                    "score": match["score"],
                    "email": user.email,
                    "profile": user.profile,
                    "matched_on": [e.embedding_type for e in match["embeddings"]]
                })

        return jsonify({
            "success": True,
            "matches": formatted_matches,
            "total": len(formatted_matches),
            "criteria": criteria,
            "requester_id": user_id
        }), 200
    except Exception as e:
        logger.error(f'Error testing matching: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


# Global variable to track generation progress
generation_progress = {
    'total': 0,
    'current': 0,
    'in_progress': False,
    'error': None
}

@fake_mentors_bp.route('/fake-mentors/progress', methods=['GET'])
def get_generation_progress():
    """Get the current progress of mentor generation"""
    global generation_progress
    return jsonify({
        'success': True,
        'total': generation_progress['total'],
        'current': generation_progress['current'],
        'in_progress': generation_progress['in_progress'],
        'error': generation_progress['error']
    })


@fake_mentors_bp.route('/fake-mentors/count', methods=['GET'])
def get_mentor_count():
    """Get the current count of mentors"""
    try:
        mentor_count = User.query.filter_by(user_type=UserType.MENTOR).count()
        return jsonify({
            "success": True,
            "count": mentor_count
        }), 200
    except Exception as e:
        logger.error(f'Error getting mentor count: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/export-json', methods=['GET'])
def export_mentors_as_json():
    """Export all mentors as JSON for testing"""
    logger.debug('Received request to export mentors as JSON')
    try:
        # Query all mentors
        mentors = User.query.filter_by(user_type="MENTOR").all()

        # Format the response
        mentor_data = []
        for mentor in mentors:
            mentor_data.append({
                "user_id": mentor.cognito_sub,
                "email": mentor.email,
                "profile": mentor.profile,
                "application_status": mentor.application_status.value if mentor.application_status else None,
                "created_at": mentor.created_at.isoformat() if mentor.created_at else None
            })

        return jsonify({
            "success": True,
            "mentors": mentor_data,
            "total": len(mentor_data)
        }), 200
    except Exception as e:
        logger.error(f'Error exporting mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500
