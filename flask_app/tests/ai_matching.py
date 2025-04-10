#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
import openai
from flask_app.extensions.embeddings import EmbeddingFactory, TheAlgorithm

def load_test_data(file_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load test data from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing test data
        
    Returns:
        Dictionary containing mentors and queries
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading test data: {str(e)}")
        sys.exit(1)

def prepare_mentor_data(mentors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare mentor data for the embedding system.
    
    Args:
        mentors: List of mentor profiles
        
    Returns:
        List of mentor profiles in the format expected by the embedding system
    """
    prepared_mentors = []
    for mentor in mentors:
        # Create a profile that matches the expected format for the embedding system
        prepared_mentor = {
            "cognito_sub": mentor["id"],  # Use the generated ID as the cognito_sub
            "profile": {
                "firstName": mentor["firstName"],
                "lastName": mentor["lastName"],
                "country": mentor["country"],
                "stateProvince": mentor["stateProvince"],
                "schoolDistrict": mentor["schoolDistrict"],
                "timeZone": mentor["timeZone"],
                "primarySubject": mentor["primarySubject"],
                "mentorSkills": mentor["mentorSkills"]
            },
            "user_type": "MENTOR",
            "is_active": True
        }
        prepared_mentors.append(prepared_mentor)
    return prepared_mentors

def prepare_query_data(query: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepare query data for the embedding system.
    
    Args:
        query: Query data
        
    Returns:
        Dictionary with query data in the format expected by the embedding system
    """
    # Create a query that matches the expected format for the embedding system
    prepared_query = {
        "primarySubject": query["primarySubject"],
        "lookingFor": query["lookingFor"],
        "entire_profile": f"Subject: {query['primarySubject']}\nLooking for: {query['lookingFor']}\nYears teaching: {query['yearsTeaching']}"
    }
    return prepared_query

def run_matching_test(test_data_path: str) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Run matching tests using the embedding system.
    
    Args:
        test_data_path: Path to the test data file
        
    Returns:
        Tuple containing (number of passed tests, total tests, detailed results)
    """
    # Load test data
    test_data = load_test_data(test_data_path)
    mentors = test_data["mentors"]
    queries = test_data["queries"]
    
    # Initialize the embedding system
    embedding_factory = EmbeddingFactory()
    algorithm = TheAlgorithm()
    
    # Prepare mentor data
    prepared_mentors = prepare_mentor_data(mentors)
    
    # Store mentor embeddings
    for mentor in prepared_mentors:
        # Generate embedding data from mentor profile
        embedding_data = {
            "firstName": mentor["profile"]["firstName"],
            "lastName": mentor["profile"]["lastName"],
            "primarySubject": mentor["profile"]["primarySubject"],
            "mentorSkills": mentor["profile"]["mentorSkills"]
        }
        
        # Store the embeddings
        embedding_factory.store_embedding(mentor["cognito_sub"], embedding_data)
    
    # Run tests for each query
    passed = 0
    total = len(queries)
    detailed_results = []
    
    for i, query in enumerate(queries):
        print(f"Testing query {i+1}/{total}...")
        
        # Prepare query data
        prepared_query = prepare_query_data(query)
        
        # Get matches using the algorithm
        matches = algorithm.get_closest_embeddings(
            "test-user-id",  # Use a dummy user ID for testing
            prepared_query,
            limit=10  # Get more than 3 to see where the target mentor ranks
        )
        
        # Check if the target mentor is in the top 3 matches
        target_mentor_id = query["targetMentorId"]
        target_in_top3 = False
        target_rank = None
        
        for rank, match in enumerate(matches[:3], 1):
            if match["user_id"] == target_mentor_id:
                target_in_top3 = True
                target_rank = rank
                break
        
        # If not in top 3, find the actual rank if present
        if not target_in_top3:
            for rank, match in enumerate(matches, 1):
                if match["user_id"] == target_mentor_id:
                    target_rank = rank
                    break
        
        # Record the result
        result = {
            "query_index": i,
            "query_name": f"{query['firstName']} {query['lastName']}",
            "target_mentor_id": target_mentor_id,
            "target_mentor_name": next((f"{m['firstName']} {m['lastName']}" for m in mentors if m["id"] == target_mentor_id), "Unknown"),
            "target_in_top3": target_in_top3,
            "target_rank": target_rank,
            "passed": target_in_top3
        }
        detailed_results.append(result)
        
        if target_in_top3:
            passed += 1
    
    return passed, total, detailed_results

def main() -> None:
    """Main function to run the matching tests."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test AI matching with generated mentor profiles and queries"
    )
    parser.add_argument("--test-data", type=str, default="matching-test-data.json", 
                        help="Path to the test data file (default: matching-test-data.json)")
    parser.add_argument("--output", type=str, default="matching-test-results.json",
                        help="Path to save the test results (default: matching-test-results.json)")
    args = parser.parse_args()

    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    # Run the matching tests
    try:
        passed, total, detailed_results = run_matching_test(args.test_data)
        
        # Calculate pass rate
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        # Print summary
        print(f"\nMatching Test Results:")
        print(f"Passed: {passed}/{total} ({pass_rate:.2f}%)")
        
        # Save detailed results to file
        results = {
            "summary": {
                "passed": passed,
                "total": total,
                "pass_rate": pass_rate
            },
            "detailed_results": detailed_results
        }
        
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Detailed results saved to {args.output}")
        
    except Exception as e:
        print(f"Error running matching tests: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
