import concurrent.futures
import os
import time
import json
import threading
import queue
import uuid
from typing import Dict, Any, List, Optional, Tuple, Callable
from openai import OpenAI
from faker import Faker
from extensions.logging import get_logger

logger = get_logger(__name__)

MODEL = 'o4-mini'

# Check for OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Create a global OpenAI client
openai_client = OpenAI(api_key=api_key)

# Thread pool for parallel processing of OpenAI API calls
openai_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=20)


def generate_mentor_profile(faker: Faker, index: int, count: int, config: Dict[str, Any]) -> Dict[
    str, Any]:
    """
    Generate a mentor profile using Faker for personal information and OpenAI for education-specific details.
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
            country = faker.country()
            state_province = faker.state()

    # Assign a specific job type based on weights
    job_types = config.get('job_types', [])
    if job_types:
        total_weight = sum(job.get('weight', 0) for job in job_types)

        if total_weight > 0:
            # Calculate how many profiles of each type to generate based on weights
            job_distributions = []
            remaining_count = count

            for job in job_types[:-1]:
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

    # Define the tool for structured profile data
    profile_tools = [
        {
            "type": "function",
            "name": "create_mentor_profile",
            "description": "Create a structured mentor profile with education-specific details",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    ]
    
    # Add all expected fields to the tool parameters
    for field in config.get('fields', []):
        field_name = field['name']
        field_desc = field['description']
        profile_tools[0]["parameters"]["properties"][field_name] = {
            "type": ["string", "null"],
            "description": field_desc
        }
        profile_tools[0]["parameters"]["required"].append(field_name)


    # Use OpenAI to generate the education-specific details with tool calling
    profile_response = openai_client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": config.get('system_prompt', ''),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        tools=profile_tools,
        tool_choice={"type": "function", "name": "create_mentor_profile"},
    )
    
    # Extract the structured data from the tool call
    profile_data = {}
    if profile_response.output and len(profile_response.output) > 0:
        for output_item in profile_response.output:
            if output_item.type == "function_call" and output_item.name == "create_mentor_profile":
                profile_data = json.loads(output_item.arguments)
                break

    # Generate a unique ID for the mentor
    mentor_id = str(uuid.uuid4())

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


def generate_matching_query(profile: Dict[str, Any], faker: Faker, index: int, count: int,
                            config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a matching query for a mentor profile using the OpenAI API.
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

    # Define the tool for structured query data
    query_tools = [
        {
            "type": "function",
            "name": "create_matching_query",
            "description": "Create a structured matching query for a mentor profile",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    ]
    
    # Add all expected fields to the tool parameters
    for field in config.get('query_fields', []):
        field_name = field['name']
        field_desc = field['description']
        query_tools[0]["parameters"]["properties"][field_name] = {
            "type": ["string", "null"],
            "description": field_desc
        }
        query_tools[0]["parameters"]["required"].append(field_name)
    
    # Use OpenAI to generate the matching query with tool calling
    query_response = openai_client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": config.get('query_system_prompt', ''),
            },
            {
                "role": "user",
                "content": query_user_prompt,
            },
        ],
        tools=query_tools,
        tool_choice={"type": "function", "name": "create_matching_query"},
    )
    
    # Extract the structured data from the tool call
    query_data = {}
    if query_response.output and len(query_response.output) > 0:
        for output_item in query_response.output:
            if output_item.type == "function_call" and output_item.name == "create_matching_query":
                query_data = json.loads(output_item.arguments)
                break

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


def worker(faker: Faker, index: int, count: int, config: Dict[str, Any],
           result_queue: queue.Queue) -> None:
    """
    Worker thread function that generates a mentor profile and matching query.
    """
    try:
        # Generate mentor profile
        profile = generate_mentor_profile(faker, index, count, config)

        # Generate matching query for this profile
        query = generate_matching_query(profile, faker, index, count, config)

        # Put results in queue
        result_queue.put((index, profile, query))

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON for item {index + 1}: {str(e)}")
    except AttributeError as e:
        logger.error(f"Error with tool calling response for item {index + 1}: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing item {index + 1}: {str(e)}")
        logger.exception(e)


def generate_mentor_profiles(num_profiles: int, config: Dict[str, Any], locale: str,
                             progress_update_callback: Callable[[int, int], None] = None) -> List[
    Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Generate mentor profiles and matching queries using OpenAI.

    Args:
        num_profiles: The number of profiles to generate
        config: Configuration dictionary with prompts and fields
        locale: Locale for Faker (e.g., 'en_US')
        progress_update_callback: Optional callback function to update progress

    Returns:
        List of tuples containing (profile, query) pairs
    """
    try:
        # Initialize Faker with the specified locale
        faker = Faker(locale)

        # Set seed for reproducibility
        Faker.seed(42)

        # Create a queue to collect results from threads
        result_queue = queue.Queue()

        # Create and start worker threads
        threads: List[threading.Thread] = []
        max_threads = min(20, num_profiles)  # Don't create more threads than items

        logger.info(f"Starting generation with {max_threads} threads for {num_profiles} education expert profiles...")

        for i in range(num_profiles):
            # Create a new thread for each item
            thread = threading.Thread(
                target=worker,
                args=(faker, i, num_profiles, config, result_queue)
            )
            threads.append(thread)
            thread.start()

            # Update progress if callback provided
            if progress_update_callback:
                progress_update_callback(i + 1, num_profiles)

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
        profiles_and_queries = [(profile, query) for _, profile, query in results]

        return profiles_and_queries

    except Exception as e:
        logger.error(f"Error generating mentor profiles: {str(e)}")
        logger.exception(e)
        raise
