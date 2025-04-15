from typing import Dict, List, Any, Optional
import openai
from flask_app.extensions.logging import get_logger
from flask_app.models.embedding import UserEmbedding
from flask_app.extensions.database import db
from flask_app.config import OpenAIConfig

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

    def generate_embedding_dict(self, user_id: str, embedding_dict: Dict[str, Any]) -> Dict[str, List[float]]:
        """
        Generate embeddings for a user without storing them in the database.
        
        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with text to generate embeddings for
            
        Returns:
            Dict[str, List[float]]: Dictionary with embedding types as keys and vector embeddings as values
        """
        # Generate embeddings for each field individually
        return self.generate_embeddings(user_id, embedding_dict)
    
    def store_embeddings_dict(self, user_id: str, embeddings_dict: Dict[str, List[float]]) -> None:
        """
        Store pre-generated embeddings in the database.
        
        Args:
            user_id: The ID of the user
            embeddings_dict: Dictionary with embedding types as keys and vector embeddings as values
            
        Returns:
            None
        """
        # Store each embedding in the database
        for embedding_type, vector_embedding in embeddings_dict.items():
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
    
    def store_embedding(self, user_id: str, embedding_dict: Dict[str, Any]) -> None:
        """
        Store embeddings in the database.
        
        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with text to generate embeddings for and store
            
        Returns:
            None
        """
        # Generate embeddings
        embeddings_dict = self.generate_embedding_dict(user_id, embedding_dict)
        
        # Store embeddings in the database
        self.store_embeddings_dict(user_id, embeddings_dict)

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
        
        Only returns embeddings for active mentors (user_type = 'MENTOR' and is_active = True).
        
        Args:
            embedding_type: The type of embedding to search for, or 'all' to search across all types
            vector: The vector to compare against
            limit: Maximum number of results to return
            
        Returns:
            List of UserEmbedding objects sorted by cosine distance
        """
        try:
            # Import User model here to avoid circular imports
            from flask_app.models.user import User, UserType, ApplicationStatus
            
            # Join with User model to filter by user_type and is_active
            if embedding_type != 'all':
                closest_embeddings = (
                    UserEmbedding.query
                    .join(User, UserEmbedding.user_id == User.cognito_sub)
                    .filter(UserEmbedding.embedding_type == embedding_type)
                    .filter(User.user_type == UserType.MENTOR)
                    .filter(User.is_active == True) # TODO: Update to use Sohini's is_active based on mentor availability
                    .order_by(UserEmbedding.vector_embedding.cosine_distance(vector))
                    .limit(limit)
                    .all()
                )
            else:
                logger.debug(f'Searching across all embedding types')
                closest_embeddings = (
                    UserEmbedding.query
                    .join(User, UserEmbedding.user_id == User.cognito_sub)
                    .filter(User.user_type == UserType.MENTOR)
                    .filter(User.is_active == True) # TODO: Update to use Sohini's is_active based on mentor availability
                    .order_by(UserEmbedding.vector_embedding.cosine_distance(vector))
                    .limit(limit)
                    .all()
                )
            logger.debug(f"Found {len(closest_embeddings)} active mentor matches for embedding type '{embedding_type}'")
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
            embedding_types = UserEmbedding.query.filter_by(user_id=user_id).distinct(UserEmbedding.embedding_type).all()
            logger.debug(f"Found {len(embedding_types)} embedding types for user {user_id}")
            logger.debug(f'Embedding types: {embedding_types}')
            return_types = []
            for embedding_type in embedding_types:
                return_types.append(embedding_type.embedding_type)
            # Extract column names from result
            return return_types
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
        assigns points based on their rank. It's used both for searching
        specific embedding types and for fallback searches across all types.
        
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
    
    def get_closest_embeddings(
        self, 
        user_id: str, 
        embedding_to_search_for: Dict[str, str], 
        limit: int = 10,
        excluded_keys: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find the closest embeddings to the given embedding dictionary.
        
        This method implements a targeted approach:
        1. For each key in embedding_to_search_for, check if that key exists in the database
        2. If the key exists, search only for that specific key
        3. If the key doesn't exist, search across all embedding types
        4. Aggregate all rankings to produce a final sorted list
        5. Exclude any keys specified in excluded_keys
        
        Args:
            user_id: The ID of the user making the search
            embedding_to_search_for: Dictionary with keys as identifiers and values as text to embed
            limit: Maximum number of results to return (default: 10)
            excluded_keys: List of keys to exclude from the search (default: None)
            
        Returns:
            A list of closest embeddings, sorted by match score (best matches first)
        """
        
        # Initialize excluded_keys if None
        if excluded_keys is None:
            excluded_keys = []
        
        # Generate embeddings for the search terms
        search_embeddings = self.embedding_factory.generate_embeddings(user_id, embedding_to_search_for)
        
        # Dictionary to store points for each user_id
        user_points = {}
        # Dictionary to store user embeddings
        user_embeddings = {}
        
        # Get all available embedding types in the database
        _available_embedding_types = UserEmbedding.query.distinct(UserEmbedding.embedding_type).all()
        available_embeddings = []
        for embedding_type in _available_embedding_types:
            available_embeddings.append(embedding_type.embedding_type)
        logger.debug(f"Available embedding types in database: {available_embeddings}")
        
        # Process each key in the search request
        for embedding_type, vector in search_embeddings.items():
            # Skip excluded keys
            if embedding_type in excluded_keys:
                logger.debug(f"Skipping excluded key: {embedding_type}")
                continue
                
            # Check if this embedding type exists in the database
            if embedding_type in available_embeddings:
                logger.debug(f"Searching for specific embedding type: {embedding_type}")
                # Process this specific embedding search
                self._process_embedding_search(
                    embedding_type,
                    vector,
                    user_points,
                    user_embeddings,
                    limit
                )
            else:
                logger.debug(f"Embedding type {embedding_type} not found in database, searching across all types")
                self._process_embedding_search(
                    'all',
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
#embedding_factory = EmbeddingFactory()
#the_algorithm = TheAlgorithm()
#logger.info(f'EmbeddingFactory initialized with model: {embedding_factory.embedding_model}')
