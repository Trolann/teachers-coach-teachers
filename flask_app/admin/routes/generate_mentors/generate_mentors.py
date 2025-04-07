#!/usr/bin/env python3
import argparse
import json
import os
import time
import threading
import queue
from typing import Dict, Any, List
from openai import OpenAI
from faker import Faker


def generate_mentor_profile(client: OpenAI, faker: Faker, index: int, count: int) -> Dict[str, Any]:
    """
    Generate a mentor profile using Faker for personal information and OpenAI for education-specific details.
    
    Args:
        client: OpenAI client instance
        faker: Faker instance for generating realistic personal information
        index: Current item index
        count: Total number of items to generate
        
    Returns:
        Dict containing the generated profile matching the application form structure
    """
    print(f"Generating profile {index + 1}/{count}...")
    
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
    # TODO: Remove magic values, update prompt to have the type of role/job be selected first according to a distribution (ie 30% should be #1, 20% #2, etc)
    # Use OpenAI to generate the education-specific details
    profile_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You generate realistic JSON data for education professionals and academic experts.",
            },
            {
                "role": "user",
                "content": f"""Generate realistic education-specific details for a teacher/mentor with the following information:

Personal Details:
- Name: {first_name} {last_name}
- Phone: {phone_number}
- Location: {state_province}, {country}

This person should be an education expert from one of these backgrounds (choose one):
1. University faculty (proffessor, department chair, etc.)
2. School district administrator or curriculum specialist
3. Education department/district administrator, cirriculum specialist, etc.
4. K-12 Public School Teacher - must be an expert with bio including multiple years/types of experience.
5. Any of the above and being retired or semi-retired.

Generate a JSON object with these fields:
- schoolDistrict: string (a realistic school district name, university, or organization for {state_province}, {country})
- timeZone: string (appropriate time zone for {state_province}, {country})
- primarySubject: string (the main subject area or specialty this person focuses on)
- mentorSkills: string (3-5 sentences written in FIRST PERSON describing your areas of expertise, teaching techniques, and specific skills you can offer as a mentor. Start with "I specialize in..." or similar first-person phrasing)

Make it diverse and realistic for an accomplished education professional who would be a good mentor for junior teachers. Return ONLY the JSON with no explanations.""",
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
    
    # Combine Faker data with OpenAI data to match the application form structure
    complete_profile = {
        "firstName": first_name,
        "lastName": last_name,
        "phoneNumber": phone_number,
        "country": country,
        "stateProvince": state_province,
        "schoolDistrict": profile_data.get("schoolDistrict", ""),
        "timeZone": profile_data.get("timeZone", ""),
        "primarySubject": profile_data.get("primarySubject", ""),
        "mentorSkills": profile_data.get("mentorSkills", "")
    }
    
    return complete_profile


def generate_matching_query(client: OpenAI, profile: Dict[str, Any], faker: Faker, index: int, count: int) -> Dict[str, Any]:
    """
    Generate a matching query for a mentor profile using the OpenAI API.
    
    Args:
        client: OpenAI client instance
        profile: The mentor profile to match against
        faker: Faker instance for generating realistic personal information
        index: Current item index
        count: Total number of items to generate
        
    Returns:
        Dict containing the generated query
    """
    print(f"Generating query {index + 1}/{count}...")
    
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
    
    query_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You generate realistic JSON data for education professionals seeking mentorship.",
            },
            {
                "role": "user",
                "content": f"""Based on this mentor profile:
            {json.dumps(profile)}
            
            Generate a search query for a junior teacher named {mentee_first_name} {mentee_last_name} from {mentee_state}, {mentee_country} 
            who would be looking for this specific mentor.
            
            The query should be a JSON object with these fields:
            - primarySubject: string (subject area the mentee teaches, should be related to the mentor's subject)
            - lookingFor: string (2-3 sentences about what specific guidance they're seeking from this mentor)
            - yearsTeaching: number (between 1-5 years)
            
            Return ONLY the JSON with no explanations.""",
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
        "primarySubject": query_data.get("primarySubject", ""),
        "lookingFor": query_data.get("lookingFor", ""),
        "yearsTeaching": query_data.get("yearsTeaching", 1)
    }
    
    return complete_query


def worker(client: OpenAI, faker: Faker, index: int, count: int, result_queue: queue.Queue) -> None:
    """
    Worker thread function that generates a mentor profile and matching query.
    
    Args:
        client: OpenAI client instance
        faker: Faker instance for generating realistic names and emails
        index: Current item index
        count: Total number of items to generate
        result_queue: Queue to store results
    """
    try:
        # Generate mentor profile
        profile = generate_mentor_profile(client, faker, index, count)
        
        # Generate matching query for this profile
        query = generate_matching_query(client, profile, faker, index, count)
        
        # Put results in queue
        result_queue.put((index, profile, query))
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for item {index + 1}: {str(e)}")
    except Exception as e:
        print(f"Error processing item {index + 1}: {str(e)}")


def main() -> None:
    """Main function to generate mentor profiles and matching queries using threading."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate fake mentor profiles and matching queries for education professionals"
    )
    parser.add_argument("count", type=int, help="Number of profiles to generate")
    parser.add_argument("--threads", type=int, default=5, help="Number of threads to use (default: 5)")
    parser.add_argument("--locale", type=str, default="en_US", help="Locale for Faker (default: en_US)")
    args = parser.parse_args()

    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    # Initialize OpenAI client and Faker
    client = OpenAI(api_key=api_key)
    faker = Faker(args.locale)
    
    # Set seed for reproducibility
    Faker.seed(42)
    
    # Files to save the generated data
    mentors_file = "fake-mentors.json"
    queries_file = "queries.json"
    
    # Use a queue to collect results from threads
    result_queue: queue.Queue = queue.Queue()
    
    # Create and start worker threads
    threads: List[threading.Thread] = []
    max_threads = min(args.threads, args.count)  # Don't create more threads than items
    
    print(f"Starting generation with {max_threads} threads for {args.count} education expert profiles...")
    
    for i in range(args.count):
        # Create a new thread for each item
        thread = threading.Thread(
            target=worker,
            args=(client, faker, i, args.count, result_queue)
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
    
    # Write results to files as JSON arrays
    with open(mentors_file, "w") as profile_file, open(queries_file, "w") as query_file:
        profiles = [profile for _, profile, _ in results]
        queries = [query for _, _, query in results]
        
        json.dump(profiles, profile_file, indent=2)
        json.dump(queries, query_file, indent=2)

    print(f"Successfully generated profiles saved to {mentors_file}")
    print(f"Successfully generated matching queries saved to {queries_file}")


if __name__ == "__main__":
    main()
