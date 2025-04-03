import os
from typing import Dict, List, Any, Optional
import openai
from flask_app.extensions.logging import get_logger

logger = get_logger(__name__)

class EmbeddingFactory:
    """
    Contains all the logic for taking in a key value pair, generating an embedding on the value
    and either storing the key-value in the database or searching the database.
    """
    
    def __init__(self):
        """Initialize the EmbeddingFactory with OpenAI API key."""
        # Get API key from environment variable or use a default for development
        self.api_key = os.environ.get("OPENAI_API_KEY") # TODO: Move to config
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Set the OpenAI API key
        openai.api_key = self.api_key
        
        # Default embedding model
        self.embedding_model = "text-embedding-3-small"
        self.openai_client = openai.OpenAI()

    def get_closest_embeddings(self, embedding_to_search_for) -> List[Any]:
        """
        Find the closest embeddings to the given embedding.
        
        Args:
            embedding_to_search_for: The embedding to search for
            
        Returns:
            A list of closest embeddings
        """
        pass

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
                embedding_key = f"{key}_embedding"
                result_dict[embedding_key] = embedding
                logger.debug(f"Generated embedding for key '{key}': {embedding_key} with length {len(embedding)}")
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
            embedding_dict: Dictionary with embeddings to store
        """
        pass

embedding_factory = EmbeddingFactory()
logger.info(f'Embedding Factory initialized with model: {embedding_factory.embedding_model}')

# Example dictionary to generate embeddings for
example_dict = {
    "bio": "I am a software engineer with experience in Python and Flask.",
    "expertise": "Machine Learning, Data Science",
    "goals": "To become a senior developer and lead projects."
}

# Generate embeddings
embedding_factory.store_embedding('1234', example_dict)
