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
from typing import Dict, List, Optional, Any, Tuple, Union
import sys
import os
import time
from openai import OpenAI
from faker import Faker
import glob
import queue

logger = get_logger(__name__)
fake_mentors_bp = Blueprint('fake_mentors', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()

# Thread pool for parallel processing of OpenAI API calls
openai_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=20)

# Path to the configuration file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'base-config.json')
GENERATE_MENTORS_DIR = os.path.join(os.path.dirname(__file__), 'generate_mentors')

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
    
    This function ONLY calls the OpenAI API and does not interact with the database.
    
    Args:
        cognito_sub: The user's cognito sub ID
        embedding_data: The data to generate embeddings from
        
    Returns:
        Optional[Dict[str, List[float]]]: Dictionary with embedding types as keys and vector embeddings as values,
                                         or None if there was an error
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
        # Map futures to cognito_sub for easier tracking
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
                # Store each embedding in the database directly without calling store_embeddings_dict
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
        num_profiles = int(request.form.get('numProfiles', 0))
        if num_profiles <= 0:
            return jsonify({'success': False, 'error': 'Number of profiles must be greater than 0'}), 400
        
        if num_profiles > 100:
            return jsonify({'success': False, 'error': 'Maximum 100 profiles can be generated at once'}), 400
        
        # Get the configuration
        config_data = request.form.get('config')
        if config_data:
            try:
                config = json.loads(config_data)
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid configuration JSON'}), 400
        else:
            config = load_config()
        
        # Get the locale for Faker
        locale = request.form.get('locale', 'en_US')
        
        # Get the auto-save options
        auto_save_file = request.form.get('autoSaveFile', 'false').lower() == 'true'
        auto_save_db = request.form.get('autoSaveDB', 'false').lower() == 'true'
        
        # Determine save option based on auto-save checkboxes
        save_option = 'none'
        if auto_save_file and auto_save_db:
            save_option = 'both'
        elif auto_save_file:
            save_option = 'file'
        elif auto_save_db:
            save_option = 'db'
        
        logger.info(f'Auto-save options: file={auto_save_file}, db={auto_save_db}, save_option={save_option}')
        
        logger.info(f'Generating {num_profiles} fake mentor profiles with locale {locale}')
        
        # Reset progress tracking
        with progress_lock:
            generation_progress['total'] = num_profiles
            generation_progress['current'] = 0
            generation_progress['in_progress'] = True
            generation_progress['error'] = None
            generation_progress['results'] = []
        
        # Start a thread to process generation
        threading.Thread(
            target=_process_openai_profile_generation, 
            args=(num_profiles, config, locale, save_option), 
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


def _process_openai_profile_generation(num_profiles: int, config: Dict[str, Any], locale: str, save_option: str) -> None:
    """
    Process profile generation using OpenAI and Faker
    
    Args:
        num_profiles: The total number of profiles to generate
        config: Configuration dictionary with prompts and fields
        locale: Locale for Faker
        save_option: Option for saving results ('none', 'db', 'file', 'both')
    """
    global generation_progress, result_queue
    
    try:
        # Check for OpenAI API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            with progress_lock:
                generation_progress['error'] = "OPENAI_API_KEY environment variable is not set"
                generation_progress['in_progress'] = False
            logger.error("OPENAI_API_KEY environment variable is not set")
            return
        
        # Initialize OpenAI client and Faker
        client = OpenAI(api_key=api_key)
        faker = Faker(locale)
        
        # Set seed for reproducibility
        Faker.seed(42)
        
        # Use a queue to collect results from threads
        while not result_queue.empty():
            result_queue.get()
        
        # Create and start worker threads
        threads: List[threading.Thread] = []
        max_threads = min(20, num_profiles)  # Don't create more threads than items
        
        logger.info(f"Starting generation with {max_threads} threads for {num_profiles} education expert profiles...")
        
        for i in range(num_profiles):
            # Create a new thread for each item
            thread = threading.Thread(
                target=worker,
                args=(client, faker, i, num_profiles, config, result_queue)
            )
            threads.append(thread)
            thread.start()
            
            # Limit the number of concurrent threads
            if len(threads) >= max_threads:
                # Wait for a thread to complete before starting a new one
                threads[0].join()
                threads.pop(0)
                
            # Add a small delay between thread starts to avoid rate limiting
            time.sleep(0.5)
        
        # Wait for all remaining threads to complete
        for thread in threads:
            thread.join()
        
        # Collect all results from the queue
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Sort results by index to maintain order
        results.sort(key=lambda x: x[0])
        
        # Extract profiles and queries
        profiles = [profile for _, profile, _ in results]
        queries = [query for _, _, query in results]
        
        # Create test data structure that includes both mentors and queries
        test_data = {
            "mentors": profiles,
            "queries": queries
        }
        
        # Store the results in the progress object
        with progress_lock:
            generation_progress['results'] = test_data
        
        # Save to file if requested
        if save_option in ['file', 'both']:
            try:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                mentors_file = os.path.join(GENERATE_MENTORS_DIR, f"fake-mentors-{timestamp}.json")
                queries_file = os.path.join(GENERATE_MENTORS_DIR, f"queries-{timestamp}.json")
                test_data_file = os.path.join(GENERATE_MENTORS_DIR, f"matching-test-data-{timestamp}.json")
                
                # Ensure directory exists
                os.makedirs(GENERATE_MENTORS_DIR, exist_ok=True)
                
                with open(mentors_file, "w") as profile_file, open(queries_file, "w") as query_file, open(test_data_file, "w") as test_file:
                    json.dump(profiles, profile_file, indent=2)
                    json.dump(queries, query_file, indent=2)
                    json.dump(test_data, test_file, indent=2)
                
                logger.info(f"Successfully generated profiles saved to {mentors_file}")
                logger.info(f"Successfully generated matching queries saved to {queries_file}")
                logger.info(f"Successfully generated test data saved to {test_data_file}")
            except Exception as e:
                logger.error(f"Error saving files: {str(e)}")
                logger.exception(e)
        
        # Save to database if requested
        if save_option in ['db', 'both']:
            try:
                logger.info(f"Auto-saving {len(profiles)} profiles to database")
                users = []
                embedding_tasks = []
                
                for profile in profiles:
                    try:
                        # Generate a unique email
                    email = profile.get('email', f"{profile['firstName'].lower()}.{profile['lastName'].lower()}@example.com")
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
                    users.append(user)
                    
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
            for user in users:
                db.session.add(user)
            
            # Flush to get IDs
            db.session.flush()
            
            # Now use thread pool to generate embeddings in parallel (only the OpenAI calls)
            # Map futures to cognito_sub for easier tracking
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
                    # Store each embedding in the database directly without calling store_embeddings_dict
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
            
            logger.info(f'Successfully auto-saved {len(users)} mentor profiles with {successful_embeddings} embeddings into database')
        
        # All profiles generated
        with progress_lock:
            generation_progress['in_progress'] = False
            logger.info(f'Successfully generated {len(profiles)} fake mentor profiles with {len(queries)} matching queries')
            logger.info(f'Save option was: {save_option}')
    except Exception as e:
        if save_option in ['db', 'both']:
            db.session.rollback()
        with progress_lock:
            generation_progress['error'] = str(e)
            generation_progress['in_progress'] = False
        logger.error(f'Error in profile generation process: {str(e)}')
        logger.exception(e)




# Functions for generating mentor profiles
def generate_mentor_profile(client: OpenAI, faker: Faker, index: int, count: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a mentor profile using Faker for personal information and OpenAI for education-specific details.
    
    Args:
        client: OpenAI client instance
        faker: Faker instance for generating realistic personal information
        index: Current item index
        count: Total number of items to generate
        config: Configuration dictionary with prompts and fields
        
    Returns:
        Dict containing the generated profile matching the application form structure
    """
    logger.debug(f"Generating profile {index + 1}/{count}...")
    
    # Generate personal information using Faker
    first_name = faker.first_name()
    last_name = faker.last_name()
    phone_number = faker.phone_number()
    
    # Get location information based on locale
    if faker.locale == 'en_US':
        country = "United States"
        state_province = faker.state()
    else:
        # For other locales, try to get appropriate region and country
        try:
            country = faker.current_country()
            state_province = faker.state()
        except:
            # Fallback if the locale doesn't support these
            country = faker.country()
            state_province = faker.state()
    
    # Assign a specific job type based on weights
    job_types = config.get('job_types', [])
    if job_types:
        # Calculate total weight
        total_weight = sum(job.get('weight', 0) for job in job_types)
        
        if total_weight > 0:
            # Calculate how many profiles of each type to generate based on weights
            job_distributions = []
            remaining_count = count
            
            for job in job_types[:-1]:  # Process all but the last job type
                job_count = int((job.get('weight', 0) / total_weight) * count)
                job_distributions.append((job['name'], job_count))
                remaining_count -= job_count
            
            # Assign the remaining count to the last job type
            if job_types:
                job_distributions.append((job_types[-1]['name'], remaining_count))
            
            # Determine which job type this profile should be
            current_index = 0
            selected_job = None
            
            for job_name, job_count in job_distributions:
                if index >= current_index and index < current_index + job_count:
                    selected_job = job_name
                    break
                current_index += job_count
            
            # If we somehow didn't assign a job (shouldn't happen), use the first one
            if selected_job is None and job_types:
                selected_job = job_types[0]['name']
                
            # Format job type for the prompt - just the selected job
            job_types_text = f"Job Type: {selected_job}\n"
        else:
            job_types_text = "No job types defined\nChoose an experienced, distinguished educator role\n"
    else:
        job_types_text = "No job types defined\nChoose an experienced, distinguished educator role\n"
    
    # Format fields for the prompt
    fields_text = ""
    for field in config.get('fields', []):
        fields_text += f"- {field['name']}: {field['description']}\n"
    
    # Prepare the user prompt with the formatted data
    user_prompt = config.get('user_prompt', '').format(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        state_province=state_province,
        country=country,
        job_types=job_types_text,
        fields=fields_text
    )
    
    # Use OpenAI to generate the education-specific details
    profile_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": config.get('system_prompt', ''),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.8,
    )

    profile_text = profile_response.choices[0].message.content.strip()
    # Handle possible markdown code blocks in the response
    if profile_text.startswith("```json"):
        profile_text = profile_text[7:].strip()
    if profile_text.endswith("```"):
        profile_text = profile_text[:-3].strip()

    # Parse the OpenAI response
    profile_data = json.loads(profile_text)
    
    # Generate a unique ID for the mentor
    mentor_id = str(uuid4())
    
    # Combine Faker data with OpenAI data to match the application form structure
    complete_profile = {
        "id": mentor_id,
        "firstName": first_name,
        "lastName": last_name,
        "phoneNumber": phone_number,
        "country": country,
        "stateProvince": state_province,
    }
    
    # Add all fields from the OpenAI response
    for field in config.get('fields', []):
        field_name = field['name']
        if field_name in profile_data:
            complete_profile[field_name] = profile_data[field_name]
    
    return complete_profile


def generate_matching_query(client: OpenAI, profile: Dict[str, Any], faker: Faker, index: int, count: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a matching query for a mentor profile using the OpenAI API.
    
    Args:
        client: OpenAI client instance
        profile: The mentor profile to match against
        faker: Faker instance for generating realistic personal information
        index: Current item index
        count: Total number of items to generate
        config: Configuration dictionary with prompts and fields
        
    Returns:
        Dict containing the generated query
    """
    logger.debug(f"Generating query {index + 1}/{count}...")
    
    # Generate mentee personal information
    mentee_first_name = faker.first_name()
    mentee_last_name = faker.last_name()
    
    # Keep mentee in same region as mentor for realistic matching
    mentee_country = profile["country"]
    
    # For US, keep in same or neighboring state
    if mentee_country == "United States":
        # 70% chance to be in same state, 30% chance to be in a different state
        if faker.random_int(min=1, max=10) <= 7:
            mentee_state = profile["stateProvince"]
        else:
            mentee_state = faker.state()
    else:
        # For other countries, use same state/province
        mentee_state = profile["stateProvince"]
    
    # Format query fields for the prompt
    query_fields_text = ""
    for field in config.get('query_fields', []):
        query_fields_text += f"- {field['name']}: {field['description']}\n"
    
    # Prepare the user prompt with the formatted data
    query_user_prompt = config.get('query_user_prompt', '').format(
        profile=json.dumps(profile),
        mentee_first_name=mentee_first_name,
        mentee_last_name=mentee_last_name,
        mentee_state=mentee_state,
        mentee_country=mentee_country,
        query_fields=query_fields_text
    )
    
    query_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": config.get('query_system_prompt', ''),
            },
            {
                "role": "user",
                "content": query_user_prompt,
            },
        ],
        temperature=0.7,
    )

    query_text = query_response.choices[0].message.content.strip()
    # Handle possible markdown code blocks in the response
    if query_text.startswith("```json"):
        query_text = query_text[7:].strip()
    if query_text.endswith("```"):
        query_text = query_text[:-3].strip()

    # Parse the OpenAI response
    query_data = json.loads(query_text)
    
    # Combine Faker data with OpenAI data
    complete_query = {
        "firstName": mentee_first_name,
        "lastName": mentee_last_name,
        "country": mentee_country,
        "stateProvince": mentee_state,
        "targetMentorId": profile["id"]  # Store the ID of the mentor this query is designed to match
    }
    
    # Add all fields from the OpenAI response
    for field in config.get('query_fields', []):
        field_name = field['name']
        if field_name in query_data:
            complete_query[field_name] = query_data[field_name]
    
    return complete_query


def worker(client: OpenAI, faker: Faker, index: int, count: int, config: Dict[str, Any], result_queue: queue.Queue) -> None:
    """
    Worker thread function that generates a mentor profile and matching query.
    
    Args:
        client: OpenAI client instance
        faker: Faker instance for generating realistic names and emails
        index: Current item index
        count: Total number of items to generate
        config: Configuration dictionary with prompts and fields
        result_queue: Queue to store results
    """
    try:
        # Generate mentor profile
        profile = generate_mentor_profile(client, faker, index, count, config)
        
        # Generate matching query for this profile
        query = generate_matching_query(client, profile, faker, index, count, config)
        
        # Put results in queue
        result_queue.put((index, profile, query))
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON for item {index + 1}: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing item {index + 1}: {str(e)}")
        logger.exception(e)

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

# Queue for collecting results from worker threads
result_queue = queue.Queue()

@fake_mentors_bp.route('/fake-mentors/progress', methods=['GET'])
def get_generation_progress():
    """Get the current progress of mentor generation"""
    global generation_progress
    
    response_data = {
        'success': True,
        'total': generation_progress['total'],
        'current': generation_progress['current'],
        'in_progress': generation_progress['in_progress'],
        'error': generation_progress['error']
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
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        if not filename:
            # Generate a filename with timestamp if not provided
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"fake-mentors-{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(GENERATE_MENTORS_DIR, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(GENERATE_MENTORS_DIR, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Successfully saved results to {file_path}")
        return jsonify({
            'success': True,
            'filename': filename,
            'path': file_path
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
                email = profile.get('email', f"{profile['firstName'].lower()}.{profile['lastName'].lower()}@example.com")
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
        # Map futures to cognito_sub for easier tracking
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
        
        logger.info(f'Successfully loaded {len(users_to_add)} mentor profiles with {successful_embeddings} embeddings into database')
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


