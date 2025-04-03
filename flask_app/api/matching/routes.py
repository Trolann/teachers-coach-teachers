from flask import Blueprint
from extensions.logging import get_logger
from extensions.embeddings import EmbeddingFactory
from flask import jsonify


matching_bp = Blueprint('matching', __name__, url_prefix='/matching')
logger = get_logger(__name__)
embedding_factory = EmbeddingFactory()

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
