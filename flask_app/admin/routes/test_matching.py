from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType
from flask_app.models.embedding import UserEmbedding
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.cognito import require_auth
from extensions.logging import get_logger
import json
import os
import glob
import datetime
from uuid import uuid4
from typing import Dict, List, Any, Tuple, Optional

logger = get_logger(__name__)
test_matching_bp = Blueprint('test_matching', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()

# Paths for files
GENERATE_MENTORS_DIR = os.path.join(os.path.dirname(__file__), 'generate_mentors')
MATCHING_TEST_RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'matching_test_results')

# Ensure directories exist
os.makedirs(GENERATE_MENTORS_DIR, exist_ok=True)
os.makedirs(MATCHING_TEST_RESULTS_DIR, exist_ok=True)

def get_json_files() -> List[str]:
    """Get a list of JSON files in the generate_mentors directory"""
    try:
        # Get all JSON files
        json_files = glob.glob(os.path.join(GENERATE_MENTORS_DIR, "*.json"))
        
        # Return just the filenames without the path
        return [os.path.basename(f) for f in json_files]
    except Exception as e:
        logger.error(f"Error getting JSON files: {str(e)}")
        return []

def validate_test_data(test_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that the test data has the correct structure.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if test_data is a dictionary
    if not isinstance(test_data, dict):
        return False, "Test data must be a JSON object"
    
    # Check if it has mentors and queries keys
    if 'mentors' not in test_data or 'queries' not in test_data:
        return False, "Test data must contain 'mentors' and 'queries' arrays"
    
    # Check if mentors and queries are lists
    if not isinstance(test_data['mentors'], list) or not isinstance(test_data['queries'], list):
        return False, "'mentors' and 'queries' must be arrays"
    
    # Check if queries have the required structure
    for i, query in enumerate(test_data['queries']):
        if not isinstance(query, dict):
            return False, f"Query at index {i} must be an object"
        
        if 'targetMentorId' not in query:
            return False, f"Query at index {i} is missing required 'targetMentorId' field"
        
        # Check if query has at least one more key besides targetMentorId
        if len(query.keys()) < 2:
            return False, f"Query at index {i} must have at least one additional field besides 'targetMentorId'"
    
    return True, None

@test_matching_bp.route('/test_matching')
@require_auth
def test_matching():
    """
    Render the test matching page with the Results tab as default.
    """
    logger.info("Rendering test matching page")
    return render_template('dashboard/test_matching.html')

@test_matching_bp.route('/test-matching/get-json-files', methods=['GET'])
def get_json_files_route():
    """Get a list of JSON files in the generate_mentors directory"""
    try:
        json_files = get_json_files()
        return jsonify({'success': True, 'files': json_files})
    except Exception as e:
        logger.error(f'Error getting JSON files: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/test', methods=['POST'])
def test_matching_algorithm():
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

def run_tests_with_data(test_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Run matching tests with the provided test data.
    
    Args:
        test_data: Dictionary containing mentors and queries
        
    Returns:
        Tuple[Dict[str, Any], Optional[str]]: (results, result_file_path)
    """
    # Import the test module functions
    from flask_app.tests.ai_matching import prepare_mentor_data, prepare_query_data
    
    # Prepare mentor data
    mentors = test_data.get('mentors', [])
    prepared_mentors = prepare_mentor_data(mentors)
    
    # Store mentor embeddings
    for mentor in prepared_mentors:
        # Generate embedding data from mentor profile
        embedding_data = {
            "firstName": mentor["profile"]["firstName"],
            "lastName": mentor["profile"]["lastName"],
            "primarySubject": mentor["profile"].get("primarySubject", ""),
            "mentorSkills": mentor["profile"].get("mentorSkills", "")
        }
        
        # Store the embeddings
        embedding_factory.store_embedding(mentor["cognito_sub"], embedding_data)
    
    # Run tests for each query
    queries = test_data.get('queries', [])
    passed = 0
    total = len(queries)
    detailed_results = []
    
    # Store all test results for saving to file
    all_test_results = []
    
    for i, query in enumerate(queries):
        logger.debug(f"Testing query {i+1}/{total}...")
        
        # Prepare query data
        prepared_query = prepare_query_data(query)
        
        # Get matches using the algorithm
        matches = the_algorithm.get_closest_embeddings(
            "test-user-id",  # Use a dummy user ID for testing
            prepared_query,
            limit=10  # Get more than 3 to see where the target mentor ranks
        )
        
        # Check if the target mentor is in the top 3 matches
        target_mentor_id = query["targetMentorId"]
        target_in_top3 = False
        target_rank = None
        
        # Get top 3 matches for audit
        top_matches = []
        for rank, match in enumerate(matches[:3], 1):
            top_matches.append({
                "rank": rank,
                "mentor_id": match["user_id"],
                "score": match["score"],
                "mentor_name": next((f"{m['firstName']} {m['lastName']}" for m in mentors if m.get("id") == match["user_id"]), "Unknown")
            })
            
            if match["user_id"] == target_mentor_id:
                target_in_top3 = True
                target_rank = rank
        
        # If not in top 3, find the actual rank if present
        if not target_in_top3:
            for rank, match in enumerate(matches, 1):
                if match["user_id"] == target_mentor_id:
                    target_rank = rank
                    break
        
        # Record the result for display
        result = {
            "query_index": i,
            "query_name": f"{query.get('firstName', '')} {query.get('lastName', '')}",
            "target_mentor_id": target_mentor_id,
            "target_mentor_name": next((f"{m['firstName']} {m['lastName']}" for m in mentors if m.get("id") == target_mentor_id), "Unknown"),
            "target_in_top3": target_in_top3,
            "target_rank": target_rank,
            "passed": target_in_top3
        }
        detailed_results.append(result)
        
        # Record detailed result for file
        test_result = {
            "query": query,
            "target_mentor_id": target_mentor_id,
            "target_mentor_name": next((f"{m['firstName']} {m['lastName']}" for m in mentors if m.get("id") == target_mentor_id), "Unknown"),
            "target_rank": target_rank,
            "passed": target_in_top3,
            "top_matches": top_matches
        }
        all_test_results.append(test_result)
        
        if target_in_top3:
            passed += 1
    
    # Calculate pass rate
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    # Format results for display
    results = {
        "summary": {
            "passed": passed,
            "total": total,
            "pass_rate": pass_rate
        },
        "detailed_results": detailed_results
    }
    
    # Save results to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"matching_test_{timestamp}.json"
    result_file_path = os.path.join(MATCHING_TEST_RESULTS_DIR, result_file)
    
    # Create full results object
    full_results = {
        "timestamp": timestamp,
        "summary": {
            "passed": passed,
            "total": total,
            "pass_rate": pass_rate
        },
        "test_results": all_test_results
    }
    
    # Save to file
    with open(result_file_path, 'w') as f:
        json.dump(full_results, f, indent=2)
    
    logger.info(f"Matching tests completed: {passed}/{total} passed ({pass_rate:.2f}%)")
    logger.info(f"Results saved to {result_file_path}")
    
    return results, result_file

@test_matching_bp.route('/test-matching/run-tests', methods=['POST'])
def run_matching_tests():
    """Run AI matching tests with uploaded test data"""
    logger.debug('Received request to run matching tests')
    try:
        # Check if file was uploaded
        if 'testDataFile' not in request.files:
            return jsonify({'success': False, 'error': 'No test data file provided'}), 400

        file = request.files['testDataFile']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Read and parse the file
        file_content = file.read().decode('utf-8')

        # Parse as JSON
        try:
            test_data = json.loads(file_content)
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Invalid JSON format: {str(e)}'}), 400

        # Validate test data structure
        is_valid, error_message = validate_test_data(test_data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        # Run the tests
        results, result_file = run_tests_with_data(test_data)
        
        return jsonify({
            "success": True, 
            "results": results,
            "resultFile": result_file
        }), 200
        
    except Exception as e:
        logger.error(f'Error running matching tests: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/run-server-file-test', methods=['POST'])
def run_server_file_test():
    """Run AI matching tests with a server-side file"""
    logger.debug('Received request to run tests with server file')
    try:
        # Get the filename from the request
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400
            
        filename = data['filename']
        file_path = os.path.join(GENERATE_MENTORS_DIR, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'File {filename} not found'}), 404
            
        # Read and parse the file
        with open(file_path, 'r') as f:
            try:
                test_data = json.load(f)
            except json.JSONDecodeError as e:
                return jsonify({'success': False, 'error': f'Invalid JSON format in {filename}: {str(e)}'}), 400
                
        # Validate test data structure
        is_valid, error_message = validate_test_data(test_data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400
            
        # Run the tests
        results, result_file = run_tests_with_data(test_data)
        
        return jsonify({
            "success": True, 
            "results": results,
            "resultFile": result_file
        }), 200
        
    except Exception as e:
        logger.error(f'Error running tests with server file: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500
