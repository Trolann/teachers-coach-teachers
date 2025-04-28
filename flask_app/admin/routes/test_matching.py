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
HUMAN_TEST_RESULTS_FILE = os.path.join(MATCHING_TEST_RESULTS_DIR, 'human-test-results.json')

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
        # Special case for fake_mentors.py format
        if 'mentors' in test_data and 'test_queries' in test_data:
            # Rename test_queries to queries for compatibility
            test_data['queries'] = test_data.pop('test_queries')
        else:
            return False, "Test data must contain 'mentors' and 'queries' arrays"
    
    # Check if mentors and queries are lists
    if not isinstance(test_data['mentors'], list) or not isinstance(test_data['queries'], list):
        return False, "'mentors' and 'queries' must be arrays"
    
    # Check if queries have the required structure
    for i, query in enumerate(test_data['queries']):
        if not isinstance(query, dict):
            return False, f"Query at index {i} must be an object"
        
        # Check for targetMentorId or target_mentor_id (support both formats)
        has_target_id = False
        if 'targetMentorId' in query:
            has_target_id = True
        elif 'target_mentor_id' in query:
            # Rename to standardized format
            query['targetMentorId'] = query.pop('target_mentor_id')
            has_target_id = True
        
        # Also check for id field that might be the target mentor ID
        if not has_target_id and 'id' in query:
            # If there's an id field but no explicit target, assume it's the target
            query['targetMentorId'] = query['id']
            has_target_id = True
            
        if not has_target_id:
            return False, f"Query at index {i} is missing required target mentor ID field"
        
        # Check if query has at least one more key besides targetMentorId
        query_fields = [k for k in query.keys() if k not in ('targetMentorId', 'id')]
        if len(query_fields) < 1:
            return False, f"Query at index {i} must have at least one field to use for matching"
    
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

@test_matching_bp.route('/test-matching/get-mentees', methods=['GET'])
def get_mentees():
    """Get a list of mentees from the database"""
    try:
        mentees = User.query.filter_by(user_type=UserType.MENTEE).all()
        mentee_list = []
        
        for mentee in mentees:
            if mentee.profile:
                name = f"{mentee.profile.get('firstName', '')} {mentee.profile.get('lastName', '')}"
                mentee_list.append({
                    "id": mentee.cognito_sub,
                    "name": name.strip() or "Unknown",
                    "email": mentee.email,
                    "profile": mentee.profile  # Include the full profile
                })
        
        return jsonify({'success': True, 'mentees': mentee_list})
    except Exception as e:
        logger.error(f'Error getting mentees: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/get-queries', methods=['POST'])
def get_queries():
    """Get queries from a server-side file"""
    try:
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400
            
        filename = data['filename']
        file_path = os.path.join(GENERATE_MENTORS_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'File {filename} not found'}), 404
            
        with open(file_path, 'r') as f:
            try:
                test_data = json.load(f)
            except json.JSONDecodeError as e:
                return jsonify({'success': False, 'error': f'Invalid JSON format in {filename}: {str(e)}'}), 400
        
        # Extract queries from the file
        queries = test_data.get('queries', [])
        if not queries:
            # Try alternate key
            queries = test_data.get('test_queries', [])
            
        if not queries:
            return jsonify({'success': False, 'error': 'No queries found in the file'}), 400
            
        # Format queries for display
        formatted_queries = []
        for i, query in enumerate(queries):
            # Extract a name if available
            name = ""
            if 'firstName' in query and 'lastName' in query:
                name = f"{query['firstName']} {query['lastName']}"
            
            formatted_queries.append({
                "id": i,
                "name": name.strip() or f"Query {i+1}",
                "data": query
            })
            
        return jsonify({'success': True, 'queries': formatted_queries})
    except Exception as e:
        logger.error(f'Error getting queries: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/save-feedback', methods=['POST'])
def save_feedback():
    """Save human feedback on match quality"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        required_fields = ['menteeId', 'menteeName', 'mentorId', 'mentorName', 'feedback', 'query']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Load existing results or create new file
        results = []
        if os.path.exists(HUMAN_TEST_RESULTS_FILE):
            try:
                with open(HUMAN_TEST_RESULTS_FILE, 'r') as f:
                    results = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupted or doesn't exist, start with empty list
                results = []
        
        # Add timestamp to the feedback
        feedback_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "menteeId": data['menteeId'],
            "menteeName": data['menteeName'],
            "mentorId": data['mentorId'],
            "mentorName": data['mentorName'],
            "feedback": data['feedback'],  # "good" or "bad"
            "query": data['query']
        }
        
        results.append(feedback_entry)
        
        # Save updated results
        with open(HUMAN_TEST_RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error saving feedback: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/save-mentee', methods=['POST'])
def save_mentee():
    """Save mentee profile to database or JSON file"""
    try:
        data = request.json
        if not data:
            logger.error("No data provided in save-mentee request")
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        save_type = data.get('saveType')
        profile_data = data.get('profileData')
        
        logger.info(f"Save mentee request received: type={save_type}, data keys={list(profile_data.keys()) if profile_data else None}")
        
        if not save_type or not profile_data:
            logger.error(f"Missing required fields: save_type={save_type}, profile_data={'present' if profile_data else 'missing'}")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
        if save_type == 'database':
            # Save to database
            mentee_id = data.get('menteeId')
            if not mentee_id:
                logger.error("Missing mentee ID for database save")
                return jsonify({'success': False, 'error': 'Missing mentee ID'}), 400
                
            logger.info(f"Saving mentee profile to database for ID: {mentee_id}")
                
            # Get the mentee from the database
            mentee = User.query.filter_by(cognito_sub=mentee_id).first()
            if not mentee:
                logger.error(f"Mentee with ID {mentee_id} not found in database")
                return jsonify({'success': False, 'error': f'Mentee with ID {mentee_id} not found'}), 404
                
            # Update the profile
            try:
                # Log the profile data we're trying to update
                logger.info(f'Updating profile for mentee {mentee_id} with data: {profile_data}')
                    
                # Get the current profile for comparison
                current_profile = mentee.profile.copy() if mentee.profile else {}
                logger.info(f'Current profile before update: {current_profile}')
                    
                # Update the profile directly
                if not mentee.profile:
                    mentee.profile = {}
                    
                # Merge the new data with existing profile
                mentee.profile.update(profile_data)
                    
                # Import db
                from flask_app.extensions.database import db
                
                # Use direct SQL update to avoid session conflicts
                try:
                    import json
                    from sqlalchemy import text
                        
                    # Convert profile to JSON string
                    profile_json = json.dumps(mentee.profile)
                        
                    # Execute direct SQL update
                    sql = text("UPDATE users SET profile = :profile WHERE cognito_sub = :cognito_sub")
                    db.session.execute(sql, {"profile": profile_json, "cognito_sub": mentee_id})
                    db.session.commit()
                    logger.info(f"Successfully updated profile for mentee {mentee_id} using SQL update")
                except Exception as sql_error:
                    logger.error(f"SQL update failed: {sql_error}")
                    logger.exception(sql_error)
                    
                    # Try to refresh the session as a fallback
                    try:
                        # Expire the object from the session
                        db.session.expire(mentee)
                        
                        # Get a fresh instance
                        fresh_mentee = User.query.filter_by(cognito_sub=mentee_id).first()
                        
                        # Update profile
                        if not fresh_mentee.profile:
                            fresh_mentee.profile = {}
                        fresh_mentee.profile.update(profile_data)
                        
                        # Save changes
                        db.session.commit()
                        logger.info(f"Successfully updated profile using session refresh approach")
                    except Exception as refresh_error:
                        logger.error(f"Session refresh approach failed: {refresh_error}")
                        logger.exception(refresh_error)
                        return jsonify({'success': False, 'error': f'Error updating profile: {str(refresh_error)}'}), 500
                    
                # Log the updated profile
                logger.info(f'Updated profile after commit: {mentee.profile}')
                    
                logger.info(f'Successfully updated profile for mentee {mentee_id}')
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f'Error updating mentee profile: {str(e)}')
                logger.exception(e)
                return jsonify({'success': False, 'error': f'Error updating profile: {str(e)}'}), 500
                
        elif save_type == 'file':
            # Save to JSON file
            file_name = data.get('fileName')
            selected_index = data.get('selectedIndex')
            
            logger.info(f"Saving mentee profile to file: {file_name}, index: {selected_index}")
            
            if not file_name or selected_index is None:
                logger.error(f"Missing file name or selected index: file_name={file_name}, selected_index={selected_index}")
                return jsonify({'success': False, 'error': 'Missing file name or selected index'}), 400
                
            file_path = os.path.join(GENERATE_MENTORS_DIR, file_name)
            if not os.path.exists(file_path):
                logger.error(f"File {file_name} not found at path: {file_path}")
                return jsonify({'success': False, 'error': f'File {file_name} not found'}), 404
                
            # Read the file
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    logger.info(f"Successfully loaded JSON file: {file_name}")
            except Exception as e:
                logger.error(f'Error reading file {file_name}: {str(e)}')
                logger.exception(e)
                return jsonify({'success': False, 'error': f'Error reading file: {str(e)}'}), 500
                
            # Update the query in the file
            queries = file_data.get('queries', [])
            if not queries:
                # Try alternate key
                queries = file_data.get('test_queries', [])
                if queries:
                    # Use the alternate key for saving
                    query_key = 'test_queries'
                    logger.info(f"Using 'test_queries' key, found {len(queries)} queries")
                else:
                    logger.error("No queries found in the file under 'queries' or 'test_queries' keys")
                    return jsonify({'success': False, 'error': 'No queries found in the file'}), 400
            else:
                query_key = 'queries'
                logger.info(f"Using 'queries' key, found {len(queries)} queries")
                
            if selected_index >= len(queries):
                logger.error(f"Selected index {selected_index} is out of range (max: {len(queries)-1})")
                return jsonify({'success': False, 'error': f'Selected index {selected_index} is out of range'}), 400
                
            # Update the query
            logger.info(f"Updating query at index {selected_index} in {query_key}")
            file_data[query_key][selected_index] = profile_data
            
            # Save the file
            try:
                with open(file_path, 'w') as f:
                    json.dump(file_data, f, indent=2)
                logger.info(f'Successfully updated query in file {file_name}')
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f'Error writing to file {file_name}: {str(e)}')
                logger.exception(e)
                return jsonify({'success': False, 'error': f'Error writing to file: {str(e)}'}), 500
        else:
            logger.error(f"Invalid save type: {save_type}")
            return jsonify({'success': False, 'error': f'Invalid save type: {save_type}'}), 400
            
    except Exception as e:
        logger.error(f'Error saving mentee profile: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500

@test_matching_bp.route('/test-matching/get-feedback-results', methods=['GET'])
def get_feedback_results():
    """Get human feedback results"""
    try:
        if not os.path.exists(HUMAN_TEST_RESULTS_FILE):
            return jsonify({'success': True, 'results': []})
            
        with open(HUMAN_TEST_RESULTS_FILE, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid JSON format in results file'}), 500
        
        # Calculate summary statistics
        total = len(results)
        good_matches = sum(1 for r in results if r.get('feedback') == 'good')
        bad_matches = total - good_matches
        
        # Group by mentee
        mentee_stats = {}
        for result in results:
            mentee_id = result.get('menteeId')
            mentee_name = result.get('menteeName', 'Unknown')
            
            if mentee_id not in mentee_stats:
                mentee_stats[mentee_id] = {
                    'name': mentee_name,
                    'total': 0,
                    'good': 0,
                    'bad': 0
                }
            
            mentee_stats[mentee_id]['total'] += 1
            if result.get('feedback') == 'good':
                mentee_stats[mentee_id]['good'] += 1
            else:
                mentee_stats[mentee_id]['bad'] += 1
        
        # Format for display
        mentee_summary = []
        for mentee_id, stats in mentee_stats.items():
            mentee_summary.append({
                'id': mentee_id,
                'name': stats['name'],
                'total': stats['total'],
                'good': stats['good'],
                'bad': stats['bad'],
                'goodPercentage': (stats['good'] / stats['total'] * 100) if stats['total'] > 0 else 0
            })
        
        return jsonify({
            'success': True, 
            'results': results,
            'summary': {
                'total': total,
                'good': good_matches,
                'bad': bad_matches,
                'goodPercentage': (good_matches / total * 100) if total > 0 else 0
            },
            'menteeStats': mentee_summary
        })
    except Exception as e:
        logger.error(f'Error getting feedback results: {str(e)}')
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
        
        # Sanitize the criteria to ensure all values are strings
        sanitized_criteria = {}
        for key, value in criteria.items():
            if value is None:
                continue
            if isinstance(value, (list, dict)):
                sanitized_criteria[key] = json.dumps(value)
            else:
                sanitized_criteria[key] = str(value)
        
        try:
            # Use the algorithm to find matches
            matches = the_algorithm.get_closest_embeddings(user_id, sanitized_criteria, limit)
        except Exception as e:
            logger.error(f"Error getting matches: {str(e)}")
            return jsonify({
                'success': False, 
                'error': f'Error generating embeddings: {str(e)}'
            }), 500

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
    # Get the mentors from the test data (for reference only, not for embedding)
    mentors = test_data.get('mentors', [])
    
    # Run tests for each query
    queries = test_data.get('queries', [])
    passed = 0
    total = len(queries)
    detailed_results = []
    
    # Store all test results for saving to file
    all_test_results = []
    
    for i, query in enumerate(queries):
        logger.debug(f"Testing query {i+1}/{total}...")
        
        # Extract the query data, removing the targetMentorId field
        search_query = {k: v for k, v in query.items() if k != 'targetMentorId'}
        
        # Generate a unique test user ID for this query
        test_user_id = f"test-user-{uuid4()}"
        
        # Sanitize the search query to ensure all values are strings
        sanitized_query = {}
        for key, value in search_query.items():
            if value is None:
                continue
            if isinstance(value, (list, dict)):
                sanitized_query[key] = json.dumps(value)
            else:
                sanitized_query[key] = str(value)
        
        try:
            # Get matches using the algorithm
            matches = the_algorithm.get_closest_embeddings(
                test_user_id,  # Use a unique user ID for each test
                sanitized_query,
                limit=10  # Get more than 3 to see where the target mentor ranks
            )
        except Exception as e:
            logger.error(f"Error getting matches for query {i+1}: {str(e)}")
            # Return empty matches if there's an error
            matches = []
        
        # Check if the target mentor is in the top 3 matches
        target_mentor_id = query["targetMentorId"]
        target_in_top3 = False
        target_rank = None
        
        # Get top 3 matches for audit
        top_matches = []
        for rank, match in enumerate(matches[:3], 1):
            # Get mentor name from database
            mentor_name = "Unknown"
            mentor_user = User.query.filter_by(cognito_sub=match["user_id"]).first()
            if mentor_user and mentor_user.profile:
                profile = mentor_user.profile
                mentor_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
            
            top_matches.append({
                "rank": rank,
                "mentor_id": match["user_id"],
                "score": match["score"],
                "mentor_name": mentor_name
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
        
        # Find target mentor name
        target_mentor_name = "Unknown"
        # First try to find in database
        target_mentor = User.query.filter_by(cognito_sub=target_mentor_id).first()
        if target_mentor and target_mentor.profile:
            profile = target_mentor.profile
            target_mentor_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        # If not found in database, try to find in test data
        else:
            for m in mentors:
                if m.get("id") == target_mentor_id or m.get("cognito_sub") == target_mentor_id:
                    target_mentor_name = f"{m.get('firstName', '')} {m.get('lastName', '')}"
                    break
        
        # Determine query name
        query_name = f"{query.get('firstName', '')} {query.get('lastName', '')}"
        if not query_name.strip():
            query_name = f"Query {i+1}"
        
        # Record the result for display
        result = {
            "query_index": i,
            "query_name": query_name,
            "target_mentor_id": target_mentor_id,
            "target_mentor_name": target_mentor_name,
            "target_in_top3": target_in_top3,
            "target_rank": target_rank,
            "passed": target_in_top3,
            "error": None if matches else "Failed to generate embeddings"
        }
        detailed_results.append(result)
        
        # Record detailed result for file
        test_result = {
            "query": query,
            "target_mentor_id": target_mentor_id,
            "target_mentor_name": target_mentor_name,
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
        
        # Check if we have mentors in the database
        mentor_count = User.query.filter_by(user_type=UserType.MENTOR).count()
        if mentor_count == 0:
            return jsonify({
                'success': False, 
                'error': 'No mentors found in the database. Please import mentors first.'
            }), 400
                
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
