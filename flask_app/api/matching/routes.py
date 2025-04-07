from flask import Blueprint, request, jsonify
from extensions.logging import get_logger
from extensions.embeddings import EmbeddingFactory, TheAlgorithm
from extensions.cognito import require_auth, CognitoTokenVerifier, parse_headers
from typing import Dict, Any, Optional


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
        token_info = parse_headers(request.headers)
        if not token_info or 'access_token' not in token_info:
            return jsonify({"error": "No valid authentication token provided"}), 401
        
        # Get user attributes from the token
        user_info = verifier.get_user_attributes(token_info['access_token'])
        if not user_info or 'sub' not in user_info:
            return jsonify({"error": "Could not retrieve user information"}), 401
        
        user_id = user_info['sub']
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
            formatted_matches.append({
                "user_id": match["user_id"],
                "score": match["score"],
                "match_strength": len(matches) - formatted_matches.index({
                    "user_id": match["user_id"],
                    "score": match["score"]
                }) if formatted_matches else len(matches),
                "matched_on": [e.embedding_type for e in match["embeddings"]]
            })
        
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
