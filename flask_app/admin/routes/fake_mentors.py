from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.logging import get_logger
from extensions.database import db
import json
from uuid import uuid4
import threading
import concurrent.futures
from typing import Dict, List, Optional

logger = get_logger(__name__)
fake_mentors_bp = Blueprint('fake_mentors', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()

# Thread pool for parallel processing of OpenAI API calls
openai_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=20)


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


def generate_embeddings(cognito_sub: str, embedding_data: Dict[str, str]) -> Optional[Dict[str, List[float]]]:
    """
    Generate embeddings for a user - this is the function that will be threaded
    
    Args:
        cognito_sub: The user's cognito sub ID
        embedding_data: The data to generate embeddings from
        
    Returns:
        Optional[Dict[str, List[float]]]: Dictionary with embedding types as keys and vector embeddings as values,
                                         or None if there was an error
    """
    try:
        embeddings_dict = embedding_factory.generate_embedding_dict(cognito_sub, embedding_data)
        logger.debug(f'Generated embeddings for user {cognito_sub}')
        return embeddings_dict
    except Exception as e:
        logger.error(f'Error generating embeddings for user {cognito_sub}: {str(e)}')
        logger.exception(e)
        return None


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

        # Parse as JSON
        try:
            profiles = json.loads(file_content)
            # Handle the case where the JSON is a dict instead of a list
            if isinstance(profiles, dict):
                profiles = [profiles]
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Invalid JSON format: {str(e)}'}), 400

        logger.info(f'Found {len(profiles)} profiles in the file')

        # Check if we have enough profiles
        if num_profiles > len(profiles):
            return jsonify({
                'success': False,
                'error': f'Requested {num_profiles} profiles but only {len(profiles)} available in file'
            }), 400

        # Limit the number of profiles to import
        profiles = profiles[:num_profiles]

        # Process all profiles and prepare data for threading
        users_to_add = []
        embedding_tasks = []
        
        for profile in profiles:
            try:
                # Validate the profile has required fields
                if not all(key in profile for key in ['firstName', 'lastName']):
                    logger.warning(f'Skipping profile missing required fields: {profile}')
                    continue

                # Create a user with mentor profile data
                # Generate a fake email if not present
                email = profile.get('email', f"{profile['firstName'].lower()}.{profile['lastName'].lower()}@example.com")
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
                users_to_add.append(user)
                
                # Prepare embedding data from profile
                embedding_data = {}

                # Add mentorSkills as bio if available
                if 'mentorSkills' in profile:
                    embedding_data['mentorSkills'] = profile['mentorSkills']

                # Add primarySubject as expertise if available
                if 'primarySubject' in profile:
                    embedding_data['primarySubject'] = profile['primarySubject']

                # Add location information
                location_parts = []
                if 'country' in profile and profile['country']:
                    location_parts.append(profile['country'])
                if 'stateProvince' in profile and profile['stateProvince']:
                    location_parts.append(profile['stateProvince'])
                if 'schoolDistrict' in profile and profile['schoolDistrict']:
                    location_parts.append(profile['schoolDistrict'])
                
                if location_parts:
                    embedding_data['location'] = ', '.join(location_parts)

                # Add any other relevant fields
                for key, value in profile.items():
                    if key not in embedding_data and isinstance(value, (str, int, float)):
                        # Convert camelCase to snake_case for consistency
                        snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
                        embedding_data[snake_key] = str(value)

                # Store the embedding data for later processing
                if embedding_data:
                    embedding_tasks.append((cognito_sub, embedding_data))
                
                logger.debug(f'Prepared imported mentor user with cognito_sub: {cognito_sub}')
            except Exception as e:
                logger.error(f'Error preparing profile: {str(e)}')
                logger.exception(e)
        
        # Add all users to the database
        for user in users_to_add:
            db.session.add(user)
        
        # Flush to get IDs
        db.session.flush()
        
        # Now use thread pool to generate embeddings in parallel (only the OpenAI calls)
        futures = []
        for cognito_sub, embedding_data in embedding_tasks:
            futures.append(openai_thread_pool.submit(generate_embeddings, cognito_sub, embedding_data))
        
        # Process results as they complete
        successful_embeddings = 0
        for future in concurrent.futures.as_completed(futures):
            embeddings_dict = future.result()
            if embeddings_dict:
                cognito_sub = ''
                # Get the cognito_sub from the completed task
                # We need to find which task this future corresponds to
                for i, (sub, _) in enumerate(embedding_tasks):
                    if futures[i].done() and futures[i] == future:
                        cognito_sub = sub
                        break
                
                # Store the embeddings in the database (in the main thread)
                try:
                    embedding_factory.store_embeddings_dict(cognito_sub, embeddings_dict)
                    successful_embeddings += 1
                except Exception as e:
                    logger.error(f'Error storing embeddings for user {cognito_sub}: {str(e)}')
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f'Successfully imported {len(users_to_add)} mentor profiles with {successful_embeddings} embeddings')
        return jsonify({'success': True, 'count': len(users_to_add)})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error importing mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


# This function is removed and replaced with the implementation below


@fake_mentors_bp.route('/fake-mentors/generate', methods=['POST'])
def generate_fake_mentors():
    """Generate fake mentor profiles using thread pool"""
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
        with progress_lock:
            generation_progress['total'] = num_profiles
            generation_progress['current'] = 0
            generation_progress['in_progress'] = True
            generation_progress['error'] = None
        
        # Start a thread to process generation
        threading.Thread(target=_process_profile_generation, args=(num_profiles,), daemon=True).start()
        
        return jsonify({
            'success': True, 
            'message': 'Profile generation started',
            'total': num_profiles
        })
    except Exception as e:
        with progress_lock:
            generation_progress['in_progress'] = False
            generation_progress['error'] = str(e)
        logger.error(f'Error starting fake mentor generation: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


def _process_profile_generation(num_profiles: int) -> None:
    """
    Process profile generation using thread pool
    
    Args:
        num_profiles: The total number of profiles to generate
    """
    global generation_progress
    
    try:
        # Create users and prepare embedding data
        users = []
        embedding_tasks = []
        
        for i in range(num_profiles):
            try:
                # Generate a unique email
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
                users.append(user)
                
                # Prepare embedding data
                embedding_data = {
                    "bio": profile["bio"],
                    "expertise": ", ".join(profile["expertise_areas"]),
                    "experience": f"{profile['years_of_experience']} years of experience",
                    "skills": ", ".join(profile["skills"])
                }
                
                # Store for later processing
                embedding_tasks.append((cognito_sub, embedding_data))
                
                # Update progress for user creation
                with progress_lock:
                    generation_progress['current'] += 0.5  # Count as half the work
                    logger.debug(f'Prepared fake mentor {i+1}/{num_profiles}')
            except Exception as e:
                logger.error(f'Error preparing mentor {i+1}: {str(e)}')
                logger.exception(e)
        
        # Add all users to the database
        for user in users:
            db.session.add(user)
        
        # Flush to get IDs
        db.session.flush()
        
        # Now use thread pool to generate embeddings in parallel (only the OpenAI calls)
        futures = []
        for cognito_sub, embedding_data in embedding_tasks:
            futures.append(openai_thread_pool.submit(generate_embeddings, cognito_sub, embedding_data))
        
        # Process results as they complete
        successful_embeddings = 0
        for future in concurrent.futures.as_completed(futures):
            embeddings_dict = future.result()
            if embeddings_dict:
                cognito_sub = ''
                # Get the cognito_sub from the completed task
                # We need to find which task this future corresponds to
                for i, (sub, _) in enumerate(embedding_tasks):
                    if futures[i].done() and futures[i] == future:
                        cognito_sub = sub
                        break
                
                # Store the embeddings in the database (in the main thread)
                try:
                    embedding_factory.store_embeddings_dict(cognito_sub, embeddings_dict)
                    successful_embeddings += 1
                    # Update progress for embedding generation
                    with progress_lock:
                        generation_progress['current'] += 0.5  # Count as the other half of the work
                except Exception as e:
                    logger.error(f'Error storing embeddings for user {cognito_sub}: {str(e)}')
        
        # Commit all changes
        db.session.commit()
        
        # All profiles generated
        with progress_lock:
            generation_progress['in_progress'] = False
            logger.info(f'Successfully generated {len(users)} fake mentor profiles with {successful_embeddings} embeddings')
    except Exception as e:
        db.session.rollback()
        with progress_lock:
            generation_progress['error'] = str(e)
            generation_progress['in_progress'] = False
        logger.error(f'Error in profile generation process: {str(e)}')
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
                # Format the profile for display
                profile = user.profile
                # Add formatted name for display
                if 'firstName' in profile and 'lastName' in profile:
                    profile['formattedName'] = f"{profile['firstName']} {profile['lastName']}"
                
                formatted_matches.append({
                    "user_id": match["user_id"],
                    "score": match["score"],
                    "email": user.email,
                    "profile": profile,
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

# Lock for thread-safe updates to generation_progress
progress_lock = threading.Lock()

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
