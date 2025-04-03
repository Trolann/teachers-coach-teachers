import os
from typing import Dict, List, Any, Optional
import openai

class EmbeddingFactory:
    """
    Contains all the logic for taking in a key value pair, generating an embedding on the value
    and either storing the key-value in the database or searching the database.
    """
    
    def __init__(self):
        """Initialize the EmbeddingFactory with OpenAI API key."""
        # Get API key from environment variable or use a default for development
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Set the OpenAI API key
        openai.api_key = self.api_key
        
        # Default embedding model
        self.embedding_model = "text-embedding-ada-002"

    def get_closest_embeddings(self, embedding_to_search_for) -> List[Any]:
        """
        Find the closest embeddings to the given embedding.
        
        Args:
            embedding_to_search_for: The embedding to search for
            
        Returns:
            A list of closest embeddings
        """
        pass

    def _generate_embedding(self, user_id: str, embedding_dict: Dict[str, str]) -> Dict[str, List[float]]:
        """
        Takes in a dictionary of key value pairs, generates embeddings on each value and returns a dict
        with the same keys with 'embedding' appended to the key and the value being the embedding.
        
        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with keys as identifiers and values as text to embed
            
        Returns:
            Dictionary with keys as original keys + '_embedding' and values as embedding vectors
        """
        result_dict = {}
        
        for key, value in embedding_dict.items():
            try:
                # Generate embedding using OpenAI API
                response = openai.Embedding.create(
                    input=value,
                    model=self.embedding_model
                )
                
                # Extract the embedding from the response
                embedding = response['data'][0]['embedding']
                
                # Store the embedding in the result dictionary
                embedding_key = f"{key}_embedding"
                result_dict[embedding_key] = embedding
                
                # Print the embedding to console (for debugging/demonstration)
                print(f"Generated embedding for key '{key}':")
                print(f"Embedding dimension: {len(embedding)}")
                print(f"First 5 values: {embedding[:5]}...")
                print(f"Last 5 values: {embedding[-5:]}...")
                
            except Exception as e:
                print(f"Error generating embedding for key '{key}': {str(e)}")
        
        return result_dict

    def generate_and_print_embedding(self, key: str, value: str) -> Optional[List[float]]:
        """
        Generate an embedding for a single key-value pair and print it to console.
        
        Args:
            key: The identifier for the text
            value: The text to generate an embedding for
            
        Returns:
            The generated embedding vector or None if there was an error
        """
        try:
            # Generate embedding using OpenAI API
            response = openai.Embedding.create(
                input=value,
                model=self.embedding_model
            )
            
            # Extract the embedding from the response
            embedding = response['data'][0]['embedding']
            
            # Print information about the embedding
            print(f"\nEmbedding for '{key}':")
            print(f"Text: '{value[:50]}{'...' if len(value) > 50 else ''}'")
            print(f"Model: {self.embedding_model}")
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
            print(f"Last 5 values: {embedding[-5:]}")
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None

    def _store_embedding(self, user_id: str, embedding_dict: Dict[str, Any]) -> None:
        """
        Store embeddings in the database.
        
        Args:
            user_id: The ID of the user
            embedding_dict: Dictionary with embeddings to store
        """
        pass

