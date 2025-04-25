from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType
from flask_app.models.embedding import UserEmbedding
from flask_app.config import EXCLUDED_EMBEDDING_FIELDS
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.logging import get_logger
from extensions.database import db
import json
from uuid import uuid4
import threading
import concurrent.futures
import queue
from typing import Dict, List, Optional, Any
import os
import time
import glob

# Import the generate_mentors module
from extensions.openai_generator import generate_mentor_profiles, openai_thread_pool

logger = get_logger(__name__)
fake_mentors_bp = Blueprint('fake_mentors', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()

# Path to the configuration file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'base-config.json')
GENERATE_MENTORS_DIR = os.path.join(os.path.dirname(__file__), 'generate_mentors')

# Global variable to track generation progress
generation_progress = {
    'total': 0,
    'current': 0,
    'in_progress': False,
    'error': None,
    'results': []
}

# Lock for thread-safe updates to generation_progress
progress_lock = threading.Lock()

# Queue for collecting results
result_queue = queue.Queue()


def load_config() -> Dict[str, Any]:
    """Load configuration from the JSON file"""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Configuration file not found at {CONFIG_FILE_PATH}")
            return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to the JSON file"""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)

        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False


def get_json_files() -> List[str]:
    """Get a list of JSON files in the generate_mentors directory"""
    try:
        # Ensure the directory exists
        os.makedirs(GENERATE_MENTORS_DIR, exist_ok=True)

        # Get all JSON files
        json_files = glob.glob(os.path.join(GENERATE_MENTORS_DIR, "*.json"))

        # Return just the filenames without the path
        return [os.path.basename(f) for f in json_files]
    except Exception as e:
        logger.error(f"Error getting JSON files: {str(e)}")
        return []


@fake_mentors_bp.route('/fake-mentors')
def fake_mentors_page():
    """Display the mentor import and matching test interface"""
    logger.debug('Accessing mentor import and matching test page')
    mentor_count = User.query.filter_by(user_type=UserType.MENTOR).count()
    logger.info(f'Current mentor count: {mentor_count}')

    # Load configuration
    config = load_config()

    # Get JSON files in the generate_mentors directory
    json_files = get_json_files()

    return render_template(
        'dashboard/fake_mentors.html',
        mentor_count=mentor_count,
        config=config,
        json_files=json_files
    )


def generate_embeddings(cognito_sub: str, embedding_data: Dict[str, str]) -> Optional[Dict[str, List[float]]]:
    """
    Generate embeddings for a user - this is the function that will be threaded
    """
    try:
        # Only call the OpenAI API part, not the database operations
        embeddings_dict = embedding_factory.generate_embeddings(cognito_sub, embedding_data)
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
                email = profile.get('email',
                                    f"{profile['firstName'].lower()}.{profile['lastName'].lower()}@example.com")
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

                # Add fields as bio if available
                for item in profile:
                    if item in EXCLUDED_EMBEDDING_FIELDS:
                        continue
                    if isinstance(profile[item], list):
                        embedding_data[item] = ', '.join(profile[item])
                    else:
                        embedding_data[item] = str(profile[item])

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
        future_to_sub = {}
        for cognito_sub, embedding_data in embedding_tasks:
            future = openai_thread_pool.submit(generate_embeddings, cognito_sub, embedding_data)
            future_to_sub[future] = cognito_sub

        # Process results as they complete
        successful_embeddings = 0
        embeddings_to_store = []  # Collect all embeddings to store in main thread

        for future in concurrent.futures.as_completed(future_to_sub.keys()):
            cognito_sub = future_to_sub[future]
            embeddings_dict = future.result()

            if embeddings_dict:
                # Collect the embeddings to store later in the main thread
                embeddings_to_store.append((cognito_sub, embeddings_dict))

        # Store all embeddings in the database (in the main thread)
        for cognito_sub, embeddings_dict in embeddings_to_store:
            try:
                # Store each embedding in the database directly
                for embedding_type, vector_embedding in embeddings_dict.items():
                    # Check if an embedding of this type already exists for this user
                    existing_embedding = UserEmbedding.query.filter_by(
                        user_id=cognito_sub,
                        embedding_type=embedding_type
                    ).first()

                    if existing_embedding:
                        # Update existing embedding
                        logger.info(f"Updating existing {embedding_type} embedding for user {cognito_sub}")
                        existing_embedding.vector_embedding = vector_embedding
                    else:
                        # Create new embedding
                        new_embedding = UserEmbedding(
                            user_id=cognito_sub,
                            embedding_type=embedding_type,
                            vector_embedding=vector_embedding
                        )
                        db.session.add(new_embedding)

                successful_embeddings += 1
            except Exception as e:
                logger.error(f'Error storing embeddings for user {cognito_sub}: {str(e)}')

        # Commit all changes
        db.session.commit()

        logger.info(
            f'Successfully imported {len(users_to_add)} mentor profiles with {successful_embeddings} embeddings')
        return jsonify({'success': True, 'count': len(users_to_add)})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error importing mentors: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/generate', methods=['POST'])
def generate_fake_mentors():
    """Generate fake mentor profiles using OpenAI and Faker"""
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
        # Handle both form data and JSON data
        if request.is_json:
            data = request.json
            num_profiles = int(data.get('numProfiles', 0))
            config_data = data.get('config')
            locale = data.get('locale', 'en_US')
        else:
            num_profiles = int(request.form.get('numProfiles', 0))
            config_data = request.form.get('config')
            locale = request.form.get('locale', 'en_US')
            
        logger.debug(f'Request data: numProfiles={num_profiles}, locale={locale}')
            
        if num_profiles <= 0:
            return jsonify({'success': False, 'error': 'Number of profiles must be greater than 0'}), 400

        if num_profiles > 100:
            return jsonify({'success': False, 'error': 'Maximum 100 profiles can be generated at once'}), 400

        # Get the configuration
        if config_data:
            try:
                config = json.loads(config_data) if isinstance(config_data, str) else config_data
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid configuration JSON'}), 400
        else:
            config = load_config()

        # Handle diverse locale
        if locale == 'diverse':
            locale = ['en_US', 'es_MX', 'fr_CA', 'it_IT', 'de_DE', 'ja_JP', 'zh_CN', 'ru_RU', 'hi_IN', 'ko_KR', 'vi_VN',
                 'tl_PH', 'ar_SA', 'fa_IR']

        logger.info(f'Generating {num_profiles} fake mentor profiles with locale {locale}')

        # Reset progress tracking - initialize with 0 to ensure bar stays empty
        with progress_lock:
            generation_progress['total'] = num_profiles
            generation_progress['current'] = 0
            generation_progress['in_progress'] = True
            generation_progress['error'] = None
            generation_progress['results'] = []
            generation_progress['generation_started'] = False  # Add flag to track when actual generation starts

        # Start a thread to process generation
        threading.Thread(
            target=_process_generation,
            args=(num_profiles, config, locale),
            daemon=True
        ).start()

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


def update_progress(current: int, total: int) -> None:
    """Update the generation progress"""
    global generation_progress
    with progress_lock:
        # Only update progress if it's actual generation progress
        if not generation_progress.get('generation_started', False):
            generation_progress['generation_started'] = True
        generation_progress['current'] = current


def _process_generation(num_profiles: int, config: Dict[str, Any], locale: str) -> None:
    """
    Process profile generation using the generate_mentors module
    """
    global generation_progress

    try:
        logger.info(f'Starting generation of {num_profiles} profiles with config: {config}')
        
        # Use the generate_mentors module to generate profiles
        profiles_and_queries = generate_mentor_profiles(
            num_profiles=num_profiles,
            config=config,
            locale=locale,
            progress_update_callback=update_progress
        )

        # Extract profiles and queries
        profiles = [profile for profile, _ in profiles_and_queries]
        queries = [query for _, query in profiles_and_queries]

        # Create test data structure that includes both mentors and queries
        test_data = {
            "mentors": profiles,
            "queries": queries
        }

        # Store the results in the progress object
        with progress_lock:
            generation_progress['results'] = test_data
            generation_progress['in_progress'] = False

        logger.info(f'Successfully generated {len(profiles)} fake mentor profiles with {len(queries)} matching queries')
    except Exception as e:
        with progress_lock:
            generation_progress['error'] = str(e)
            generation_progress['in_progress'] = False
        logger.error(f'Error in profile generation process: {str(e)}')
        logger.exception(e)



@fake_mentors_bp.route('/fake-mentors/progress', methods=['GET'])
def get_generation_progress():
    """Get the current progress of mentor generation"""
    global generation_progress

    response_data = {
        'success': True,
        'total': generation_progress['total'],
        'current': generation_progress['current'],
        'in_progress': generation_progress['in_progress'],
        'error': generation_progress['error'],
        'generation_started': generation_progress.get('generation_started', False)  # Include generation_started flag
    }

    # Include results if generation is complete and results are requested
    include_results = request.args.get('include_results', 'false').lower() == 'true'
    if include_results and not generation_progress['in_progress'] and generation_progress['results']:
        response_data['results'] = generation_progress['results']

    return jsonify(response_data)


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


@fake_mentors_bp.route('/fake-mentors/update-config', methods=['POST'])
def update_config():
    """Update the configuration file"""
    try:
        config_data = request.json
        if not config_data:
            return jsonify({'success': False, 'error': 'No configuration data provided'}), 400

        # Save the configuration
        success = save_config(config_data)
        if success:
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
    except Exception as e:
        logger.error(f'Error updating configuration: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/get-config', methods=['GET'])
def get_config():
    """Get the current configuration"""
    try:
        config = load_config()
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f'Error getting configuration: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/get-json-files', methods=['GET'])
def get_json_files_route():
    """Get a list of JSON files in the generate_mentors directory"""
    try:
        json_files = get_json_files()
        return jsonify({'success': True, 'files': json_files})
    except Exception as e:
        logger.error(f'Error getting JSON files: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/load-json-file', methods=['POST'])
def load_json_file():
    """Load a JSON file from the generate_mentors directory"""
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        file_path = os.path.join(GENERATE_MENTORS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'File {filename} not found'}), 404

        with open(file_path, 'r') as f:
            data = json.load(f)

        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f'Error loading JSON file: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/save-to-file', methods=['POST'])
def save_results_to_file():
    """Save generated results to a file"""
    logger.debug('Received request to save results to file')
    try:
        # Get the data and filename from the request
        data = request.json.get('data')
        filename = request.json.get('filename')
        file_format = request.json.get('format', 'both')  # Default to both formats

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Ensure directory exists
        os.makedirs(GENERATE_MENTORS_DIR, exist_ok=True)
        
        saved_files = []
        
        # Save in original format if requested
        if file_format in ['original', 'both']:
            if not filename:
                # Generate a filename with timestamp
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                original_filename = f"fake-mentors-{timestamp}.json"
            else:
                original_filename = filename
                
            original_file_path = os.path.join(GENERATE_MENTORS_DIR, original_filename)
            with open(original_file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            saved_files.append({
                'format': 'original',
                'filename': original_filename,
                'path': original_file_path
            })
            logger.info(f"Successfully saved results to {original_file_path}")
            
        # Save in matching-test-data format if requested
        if file_format in ['matching', 'both']:
            # Generate a filename with ISO timestamp
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            matching_filename = f"matching-test-data-{timestamp}.json"
            
            matching_file_path = os.path.join(GENERATE_MENTORS_DIR, matching_filename)
            with open(matching_file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            saved_files.append({
                'format': 'matching',
                'filename': matching_filename,
                'path': matching_file_path
            })
            logger.info(f"Successfully saved results to {matching_file_path}")

        return jsonify({
            'success': True,
            'files': saved_files
        })
    except Exception as e:
        logger.error(f'Error saving results to file: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@fake_mentors_bp.route('/fake-mentors/load-to-db', methods=['POST'])
def load_results_to_db():
    """Load generated results into the database"""
    logger.debug('Received request to load results into database')
    try:
        # Get the data from the request
        data = request.json.get('data')

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Extract profiles from the data
        profiles = data.get('mentors', [])

        if not profiles:
            return jsonify({'success': False, 'error': 'No mentor profiles found in data'}), 400

        # Process all profiles
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
                email = profile.get('email',
                                    f"{profile['firstName'].lower()}.{profile['lastName'].lower()}@example.com")
                cognito_sub = profile.get('id', str(uuid4()))  # Use existing ID or generate new one

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

                # Add fields as embedding data
                for field_name, field_value in profile.items():
                    if field_name in EXCLUDED_EMBEDDING_FIELDS:
                        continue
                    if isinstance(field_value, list):
                        embedding_data[field_name] = ', '.join(field_value)
                    else:
                        embedding_data[field_name] = str(field_value)

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
        future_to_sub = {}
        for cognito_sub, embedding_data in embedding_tasks:
            future = openai_thread_pool.submit(generate_embeddings, cognito_sub, embedding_data)
            future_to_sub[future] = cognito_sub

        # Process results as they complete
        successful_embeddings = 0
        embeddings_to_store = []  # Collect all embeddings to store in main thread

        for future in concurrent.futures.as_completed(future_to_sub.keys()):
            cognito_sub = future_to_sub[future]
            embeddings_dict = future.result()

            if embeddings_dict:
                # Collect the embeddings to store later in the main thread
                embeddings_to_store.append((cognito_sub, embeddings_dict))

        # Store all embeddings in the database (in the main thread)
        for cognito_sub, embeddings_dict in embeddings_to_store:
            try:
                # Store each embedding in the database directly
                for embedding_type, vector_embedding in embeddings_dict.items():
                    # Check if an embedding of this type already exists for this user
                    existing_embedding = UserEmbedding.query.filter_by(
                        user_id=cognito_sub,
                        embedding_type=embedding_type
                    ).first()

                    if existing_embedding:
                        # Update existing embedding
                        logger.info(f"Updating existing {embedding_type} embedding for user {cognito_sub}")
                        existing_embedding.vector_embedding = vector_embedding
                    else:
                        # Create new embedding
                        new_embedding = UserEmbedding(
                            user_id=cognito_sub,
                            embedding_type=embedding_type,
                            vector_embedding=vector_embedding
                        )
                        db.session.add(new_embedding)

                successful_embeddings += 1
            except Exception as e:
                logger.error(f'Error storing embeddings for user {cognito_sub}: {str(e)}')

        # Commit all changes
        db.session.commit()

        logger.info(
            f'Successfully loaded {len(users_to_add)} mentor profiles with {successful_embeddings} embeddings into database')
        return jsonify({
            'success': True,
            'count': len(users_to_add),
            'embeddings': successful_embeddings
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error loading results into database: {str(e)}')
        logger.exception(e)
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
