from typing import Dict, List, Any
import openai
from flask_app.extensions.logging import get_logger
from flask_app.models.embedding import UserEmbedding
from extensions.database import db
from config import OpenAIConfig

logger = get_logger(__name__)

class EmbeddingFactory:
    """
    Contains all the logic for taking in a key value pair, generating an embedding on the value
    and either storing the key-value in the database or searching the database.
    """
    
    def __init__(self):
        """Initialize the EmbeddingFactory with OpenAI API key."""
        # Get API key from environment variable or use a default for development
        config = OpenAIConfig()
        self.api_key = config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Set the OpenAI API key
        openai.api_key = self.api_key
        
        # Default embedding model
        self.embedding_model = "text-embedding-3-small"
        self.embedding_model = config.EMBEDDING_MODEL
        self.openai_client = openai.OpenAI()

    def get_closest_embeddings(self, user_id, embedding_to_search_for: Dict[str, str], limit: int = 10) -> List[Any]:
        """
        Find the closest embeddings to the given embedding dictionary. Returns up to 10 closest embeddings.
        
        For each key in the input dictionary:
        1. Generate an embedding for the value
        2. Find the closest embeddings in the database
        3. Assign points based on rank (1st place = 1 point, 2nd place = 2 points, etc.)
        4. Group by user_id and sum the points
        5. Sort by total points (lowest is best)
        
        Args:
            embedding_to_search_for: Dictionary with keys as identifiers and values as text to embed
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            A list of closest embeddings, sorted by match score (best matches first)
        """
        if not embedding_to_search_for:
            logger.warning("Empty embedding dictionary provided to get_closest_embeddings")
            return []
        
        # Generate embeddings for the search terms
        search_embeddings = self._generate_embeddings(user_id, embedding_to_search_for)
        
        # Dictionary to store points for each user_id
        user_points = {}
        # Dictionary to store user embeddings
        user_embeddings = {}
        
        # For each embedding type in the search dictionary
        for embedding_type, vector in search_embeddings.items():
            try:
                # Query to find the closest embeddings for this type
                closest_embeddings = (
                    UserEmbedding.query
                    .filter_by(embedding_type=embedding_type)
                    .order_by(UserEmbedding.vector_embedding.cosine_distance(vector))
                    .limit(limit)
                    .all()
                )
                
                # Assign points based on rank (1st = 1 point, 2nd = 2 points, etc.)
                for rank, embedding in enumerate(closest_embeddings, 1):
                    if embedding.user_id not in user_points:
                        user_points[embedding.user_id] = 0
                        user_embeddings[embedding.user_id] = []
                    
                    # Add points (lower is better)
                    user_points[embedding.user_id] += rank
                    
                    # Store the embedding
                    user_embeddings[embedding.user_id].append(embedding)
                    
                logger.debug(f"Found {len(closest_embeddings)} matches for embedding type '{embedding_type}'")
            except Exception as e:
                logger.error(f"Error finding closest embeddings for type '{embedding_type}': {str(e)}")
        
        # Sort users by total points (lowest is best)
        sorted_users = sorted(user_points.items(), key=lambda x: x[1])
        
        # Prepare the result list
        result = []
        for user_id, points in sorted_users:
            if user_id in user_embeddings:
                # Add user embeddings with their score
                result.append({
                    "user_id": user_id,
                    "score": points,
                    "embeddings": user_embeddings[user_id]
                })
        
        logger.info(f"Completed embedding search with {len(embedding_to_search_for)} criteria, found {len(result)} matches")
        return result[:limit]

    def _generate_embeddings(self, user_id, embedding_dict: Dict[str, str]) -> Dict[str, List[float]]:
        """
        Takes in a dictionary of key value pairs, generates embeddings on each value and returns a dict
        with the same keys with 'embedding' appended to the key and the value being the embedding.
        
        Args:
            user_id: The ID of the user - prevents abuse on the OpenAI end
            embedding_dict: Dictionary with keys as identifiers and values as text to embed
            
        Returns:
            Dictionary with keys as original keys + '_embedding' and values as embedding vectors
        """
        result_dict = {}
        
        for key, value in embedding_dict.items():
            try:
                # Generate embedding using OpenAI API
                logger.debug(f'_generate_embeddings for key: {key} with value: {value}')
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=value,
                    user=user_id
                )
                
                # Extract the embedding from the response
                embedding = response.data[0].embedding
                
                # Store the embedding in the result dictionary
                result_dict[key] = embedding
                logger.debug(f"Generated embedding for key '{key}' with length {len(embedding)}")
            except Exception as e:
                print(f"Error generating embedding for key '{key}': {str(e)}")

        logger.info(f'generate_embeddings completed for user {user_id}, created {len(result_dict)} embeddings')
        return result_dict

    def _print_embeddings(self, user_id, embedding_dict: Dict[str, str]) -> None:
        """
        Print the generated embeddings.

        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with keys as identifiers and values as embedding vectors
        """

        # generate the embeddings
        generated = self._generate_embeddings(user_id, embedding_dict)

        # Print the generated embeddings
        for key, value in generated.items():
            logger.debug(f"{key}: {len(value)}")

    def store_embedding(self, user_id: str, embedding_dict: Dict[str, Any]) -> None:
        """
        Store embeddings in the database.
        
        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with text to generate embeddings for and store
            
        Returns:
            None
        """
        # Generate embeddings for the provided text
        embeddings = self._generate_embeddings(user_id, embedding_dict)

        # Store each embedding in the database
        for key, value in embedding_dict.items():
            if key in embeddings:
                embedding_type = key
                vector_embedding = embeddings[key]
                
                # Check if an embedding of this type already exists for this user
                existing_embedding = UserEmbedding.query.filter_by(
                    user_id=user_id,
                    embedding_type=embedding_type
                ).first()

                if existing_embedding:
                    # Update existing embedding
                    logger.info(f"Updating existing {embedding_type} embedding for user {user_id}")
                    existing_embedding.vector_embedding = vector_embedding
                else:
                    # Create new embedding
                    new_embedding = UserEmbedding(
                        user_id=user_id,
                        embedding_type=embedding_type,
                        vector_embedding=vector_embedding
                    )
                    db.session.add(new_embedding)
                    
        # Commit all changes to the database
        try:
            db.session.commit()
            logger.info(f"Successfully stored embeddings for user {user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing embeddings for user {user_id}: {str(e)}")
            raise

logger.info(f'EmbeddingFactory initialized with model: {EmbeddingFactory().embedding_model}')
