from typing import Dict, List, Any, Optional
import openai
from flask_app.extensions.logging import get_logger
from flask_app.models.embedding import UserEmbedding
from extensions.database import db
from config import OpenAIConfig

logger = get_logger(__name__)

class EmbeddingFactory:
    """
    Responsible for generating and storing embeddings.
    
    This class is implemented as a singleton to ensure only one instance exists.
    """
    
    _instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(EmbeddingFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the EmbeddingFactory with OpenAI API key (only once)."""
        # Skip initialization if already initialized
        if hasattr(self, '_initialized') and self._initialized:
            return
            
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
        
        # Mark as initialized
        self._initialized = True

    def generate_embeddings(self, user_id, embedding_dict: Dict[str, str]) -> Dict[str, List[float]]:
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

    def print_embeddings(self, user_id, embedding_dict: Dict[str, str]) -> None:
        """
        Print the generated embeddings.

        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with keys as identifiers and values as embedding vectors
        """

        # generate the embeddings
        generated = self.generate_embeddings(user_id, embedding_dict)

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
        entire_profile = "\n\n".join([f"{key}: {value}" for key, value in embedding_dict.items()])
        embedding_dict["entire_profile"] = entire_profile

        embeddings = self.generate_embeddings(user_id, embedding_dict)

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

class TheAlgorithm:
    """
    Responsible for searching and ranking embeddings to find the best matches.
    
    This class handles the search logic for finding matches based on embeddings
    and ranks the results to return a final list of the best matches.
    
    This class is implemented as a singleton to ensure only one instance exists.
    """
    
    _instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(TheAlgorithm, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the EmbeddingFactory with OpenAI API key (only once)."""
        # Skip initialization if already initialized
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.embedding_factory = EmbeddingFactory()
        
        # Mark as initialized
        self._initialized = True
    
    def _find_closest_embeddings_for_vector(self, embedding_type: str, vector: List[float],  limit: int = 10) -> List[UserEmbedding]:
        """
        Helper method to find the closest embeddings for a specific vector.
        
        Args:
            embedding_type: The type of embedding to search for
            vector: The vector to compare against
            limit: Maximum number of results to return
            
        Returns:
            List of UserEmbedding objects sorted by cosine distance
        """
        try:
            closest_embeddings = (
                UserEmbedding.query
                .filter_by(embedding_type=embedding_type)
                .order_by(UserEmbedding.vector_embedding.cosine_distance(vector))
                .limit(limit)
                .all()
            )
            logger.debug(f"Found {len(closest_embeddings)} matches for embedding type '{embedding_type}'")
            return closest_embeddings
        except Exception as e:
            logger.error(f"Error finding closest embeddings for type '{embedding_type}': {str(e)}")
            return []
    
    def _assign_points_for_embeddings(
        self, 
        embeddings: List[UserEmbedding], 
        user_points: Dict[str, int], 
        user_embeddings: Dict[str, List[UserEmbedding]]
    ) -> None:
        """
        Helper method to assign points based on embedding ranks.
        
        Args:
            embeddings: List of UserEmbedding objects
            user_points: Dictionary to store points for each user_id
            user_embeddings: Dictionary to store user embeddings
            
        Returns:
            None (updates the dictionaries in place)
        """
        for rank, embedding in enumerate(embeddings, 1):
            if embedding.user_id not in user_points:
                user_points[embedding.user_id] = 0
                user_embeddings[embedding.user_id] = []
            
            # Add points (lower is better)
            user_points[embedding.user_id] += rank
            
            # Store the embedding
            user_embeddings[embedding.user_id].append(embedding)
    
    def _get_user_embedding_types(self, user_id: str) -> List[str]:
        """
        Get all embedding types available for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of embedding type strings
        """
        try:
            embedding_types = (
                db.session.query(UserEmbedding.embedding_type)
                .filter_by(user_id=user_id)
                .distinct()
                .all()
            )
            # Extract column names from result
            return [et[0] for et in embedding_types]
        except Exception as e:
            logger.error(f"Error getting embedding types for user {user_id}: {str(e)}")
            return []
    
    def _prepare_result_list(
        self, 
        user_points: Dict[str, int], 
        user_embeddings: Dict[str, List[UserEmbedding]], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Prepare the final result list sorted by points.
        
        Args:
            user_points: Dictionary with points for each user_id
            user_embeddings: Dictionary with embeddings for each user_id
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with user_id, score, and embeddings
        """
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
        
        return result[:limit]
    
    def _process_embedding_search(
        self,
        embedding_type: str,
        vector: List[float],
        user_points: Dict[str, int],
        user_embeddings: Dict[str, List[UserEmbedding]],
        limit: int = 10
    ) -> None:
        """
        Helper method to process a single embedding search and update rankings.
        
        This method finds the closest embeddings for a given vector and
        assigns points based on their rank.
        
        Args:
            embedding_type: The type of embedding to search for
            vector: The vector to compare against
            user_points: Dictionary to store points for each user_id
            user_embeddings: Dictionary to store user embeddings
            limit: Maximum number of results to return
            
        Returns:
            None (updates the dictionaries in place)
        """
        # Find closest embeddings for this vector
        closest_embeddings = self._find_closest_embeddings_for_vector(
            embedding_type,
            vector,
            limit
        )
        
        # Assign points based on rank
        self._assign_points_for_embeddings(closest_embeddings, user_points, user_embeddings)
    
    def get_closest_embeddings(self, user_id: str, embedding_to_search_for: Dict[str, str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find the closest embeddings to the given embedding dictionary.
        
        This method implements a two-step approach:
        1. First, query the DB to get all vector keys the current user has
        2. For each key, perform searching and ranking
        3. For each key in embedding_to_search_for, encode and search across the entire vector database
        4. Aggregate all rankings to produce a final sorted list
        
        Args:
            user_id: The ID of the user making the search
            embedding_to_search_for: Dictionary with keys as identifiers and values as text to embed
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            A list of closest embeddings, sorted by match score (best matches first)
        """
        
        # Generate embeddings for the search terms
        search_embeddings = self.embedding_factory.generate_embeddings(user_id, embedding_to_search_for)
        
        # Dictionary to store points for each user_id
        user_points = {}
        # Dictionary to store user embeddings
        user_embeddings = {}
        
        # Step 1: Get all embedding types for the current user
        user_embedding_types = self._get_user_embedding_types(user_id)
        logger.debug(f"Found {len(user_embedding_types)} embedding types for user {user_id}")
        
        # Step 2: For each embedding type the user has, find closest matches
        for embedding_type in user_embedding_types:
            # Get the user's embedding for this type
            user_embedding = UserEmbedding.query.filter_by(
                user_id=user_id,
                embedding_type=embedding_type
            ).first()
            
            if user_embedding:
                # Process this embedding search
                self._process_embedding_search(
                    embedding_type,
                    user_embedding.vector_embedding,
                    user_points,
                    user_embeddings,
                    limit
                )
        
        # Step 3: For each key in embedding_to_search_for, search across all vectors
        if search_embeddings:
            for embedding_type, vector in search_embeddings.items():
                # Process this embedding search
                self._process_embedding_search(
                    embedding_type,
                    vector,
                    user_points,
                    user_embeddings,
                    limit
                )
        
        # Step 4: Prepare and return the final result list
        result = self._prepare_result_list(user_points, user_embeddings, limit)
        
        logger.info(f"Completed embedding search with {len(embedding_to_search_for)} criteria, found {len(result)} matches")
        return result

# Create the singleton instances
embedding_factory = EmbeddingFactory()
the_algorithm = TheAlgorithm()
logger.info(f'EmbeddingFactory initialized with model: {embedding_factory.embedding_model}')
