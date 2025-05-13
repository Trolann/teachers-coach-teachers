from flask import Blueprint, request, jsonify
from flask_app.api.users.routes import get_user_from_token
from models.user import User
from extensions.logging import get_logger
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.cognito import require_auth, CognitoTokenVerifier, parse_headers
from extensions.matches import mentee_to_mentor_matches, submit_mentee_request, get_requests_for_mentor

matching_bp = Blueprint('matching', __name__, url_prefix='/matching')
logger = get_logger(__name__)
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()
verifier = CognitoTokenVerifier()

@matching_bp.route('/find_matches', methods=['POST'])
@require_auth
def find_matches():
    """
    Find matches for the current user based on provided criteria.
    
    Request body should contain a JSON object with keys representing
    the criteria to match on, and values as the text to match.
    
    Example:
    {
        "skills": "Python, JavaScript, React",
        "interests": "Machine Learning, Web Development",
        "goals": "Improve coding skills, learn new technologies"
    }
    
    Returns:
        A JSON object with matched users sorted by relevance
    """
    try:
        # Get the current user from the token
        user = get_user_from_token(request.headers)
        if not user or not hasattr(user, 'cognito_sub'):
            return jsonify({"error": "Could not retrieve user from token"}), 401

        user_id = user.cognito_sub
        logger.info(f"Finding matches for user {user_id}")
        
        user_id = user.cognito_sub
        logger.info(f"Finding matches for user {user_id}")
        
        # Get the search criteria from the request body
        search_criteria = request.json
        if not search_criteria or not isinstance(search_criteria, dict):
            return jsonify({"error": "Invalid search criteria. Expected JSON object with search terms."}), 400
        
        # Get the limit parameter from query string, default to 10
        try:
            limit = int(request.args.get('limit', 10))
            if limit < 1 or limit > 50:
                limit = 10  # Reset to default if out of reasonable range
        except ValueError:
            limit = 10
        
        # Find matches using the algorithm
        matches = the_algorithm.get_closest_embeddings(user_id, search_criteria, limit)
        
        # Format the response
        formatted_matches = []
        for match in matches:
            # Extract only necessary information to return to the client
            # TODO: Add additional data about the mentor (name, profile picture, etc.)
            formatted_matches.append({
                "user_id": match["user_id"],
                "score": match["score"],
                "match_strength": len(matches) - formatted_matches.index({
                    "user_id": match["user_id"],
                    "score": match["score"]
                }) if formatted_matches else len(matches),
                "matched_on": [e.embedding_type for e in match["embeddings"]]
            })
        
        # Save mentor IDs for this mentee
        mentee_to_mentor_matches[user_id] = [match["user_id"] for match in formatted_matches]
        logger.info(f"Saved {len(mentee_to_mentor_matches[user_id])} matches for mentee {user_id}")

        return jsonify({
            "matches": formatted_matches,
            "total": len(formatted_matches)
        }), 200
        
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        return jsonify({"error": f"Failed to find matches: {str(e)}"}), 500

@matching_bp.route('/debug_embeddings', methods=['GET'])
def debug_test_embeddings():
    """
    Test function to debug embeddings
    """
    logger.debug("Debugging embeddings")
    logger.info(f'Embedding Factory initialized with model: {embedding_factory.embedding_model}')

    # Example dictionary to generate embeddings for
    example_dict = {
        "bio": "I am a software engineer with experience in Python and Flask.",
        "expertise": "Machine Learning, Data Science",
        "goals": "To become a senior developer and lead projects."
    }

    # Generate embeddings
    try:
        embedding_factory.store_embedding('64781478-80c1-70fa-1144-5df7965b1428', example_dict)
        return "Embeddings generated and stored successfully", 200
    except Exception as e:
        logger.error(f"Error generating or storing embeddings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@matching_bp.route('/get_matches_for_mentee', methods=['GET'])
@require_auth
def get_matches_for_mentee():
    """
    Get mentor matches for a mentee
    """
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not found or invalid token'}), 401

    mentee_id = user.cognito_sub
    mentor_ids = mentee_to_mentor_matches.get(mentee_id, [])

    mentor_profiles = []

    for mentor_id in mentor_ids:
        mentor = User.get_by_id(mentor_id)
        if not mentor or not mentor.profile:
            continue

        profile = mentor.profile
        
        mentor_profiles.append({
            'user_id': mentor.cognito_sub,
            'firstName': profile.get('firstName'),
            'lastName': profile.get('lastName'),
            'county': profile.get('county'),
            'state_province': profile.get('state_province'),
            'country': profile.get('country'),
            'primarySubject': profile.get('primarySubject'),
        })

    return jsonify({'matches': mentor_profiles}), 200

@matching_bp.route('/mentee_request', methods=['POST'])
@require_auth
def mentee_request():
    """
    Mentee submits a request to enter a session with a mentor.
    Requires JSON body with 'mentor_id'.
    """
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    mentee_id = user.cognito_sub
    data = request.get_json()

    mentor_id = data.get('mentor_id')
    if not mentor_id:
        return jsonify({'error': 'mentor_id is required'}), 400

    try:
        submit_mentee_request(mentor_id, mentee_id)
        logger.info(f"Mentee {mentee_id} submitted request to mentor {mentor_id}")
        return jsonify({'message': 'Request submitted successfully'}), 200
    except Exception as e:
        logger.error(f"Error submitting request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/get_mentee_requests', methods=['GET'])
@require_auth
def get_mentee_requests():
    """
    Fetches a list of mentees who have requested to meet the authenticated mentor.
    """
    user = get_user_from_token(request.headers)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        mentor_id = user.cognito_sub
        mentee_ids = get_requests_for_mentor(mentor_id)

        mentees = []
        for mentee_id in mentee_ids:
            mentee = User.get_by_id(mentee_id)
            if not mentee or not mentee.profile:
                continue
            profile = mentee.profile

            mentees.append({
                'user_id': mentee.cognito_sub,
                'firstName': profile.get('firstName'),
                'lastName': profile.get('lastName'),
                'county': profile.get('county'),
                'state_province': profile.get('state_province'),
                'country': profile.get('country'),
                'primarySubject': profile.get('primarySubject'),
            })

        return jsonify({'mentee_requests': mentees}), 200
    except Exception as e:
        logger.error(f"Error retrieving mentee requests: {str(e)}")
        return jsonify({'error': str(e)}), 500