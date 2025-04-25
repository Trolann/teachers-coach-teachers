from flask import Blueprint, render_template, request, jsonify
from flask_app.models.user import User, UserType
from flask_app.models.embedding import UserEmbedding
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.cognito import require_auth
from extensions.logging import get_logger
import json
from uuid import uuid4
from typing import Dict, List, Any

logger = get_logger(__name__)
test_matching_bp = Blueprint('test_matching', __name__)

# Get instances of embedding classes
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()

@test_matching_bp.route('/test_matching')
@require_auth
def test_matching():
    """
    Render the test matching page with the Results tab as default.
    """
    logger.info("Rendering test matching page")
    return render_template('dashboard/test_matching.html')

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
        if not isinstance(test_data, dict) or 'mentors' not in test_data or 'queries' not in test_data:
            return jsonify({
                'success': False, 
                'error': 'Invalid test data format. Must contain "mentors" and "queries" arrays.'
            }), 400

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
                "primarySubject": mentor["profile"]["primarySubject"],
                "mentorSkills": mentor["profile"]["mentorSkills"]
            }
            
            # Store the embeddings
            embedding_factory.store_embedding(mentor["cognito_sub"], embedding_data)
        
        # Run tests for each query
        queries = test_data.get('queries', [])
        passed = 0
        total = len(queries)
        detailed_results = []
        
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
        
        # Calculate pass rate
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        # Format results
        results = {
            "summary": {
                "passed": passed,
                "total": total,
                "pass_rate": pass_rate
            },
            "detailed_results": detailed_results
        }
        
        logger.info(f"Matching tests completed: {passed}/{total} passed ({pass_rate:.2f}%)")
        return jsonify({"success": True, "results": results}), 200
        
    except Exception as e:
        logger.error(f'Error running matching tests: {str(e)}')
        logger.exception(e)
        return jsonify({'success': False, 'error': str(e)}), 500
