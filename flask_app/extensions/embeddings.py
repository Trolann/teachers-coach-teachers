

class EmbeddingFactory:
    """
    Contains all the logic for taking in a key value pair, generating an embedding on the value
    and either storing the key-value in the database or searching the database.
    """

    def get_closest_embeddings(self, embedding_to_search_for) -> list:
        pass

    def _generate_embedding(self, user_id, embedding_dict) -> list:
        """
        Takes in a dictionary of key value pairs, generatings embeddings on each value and returns a dict
        with the same keys with 'embedding' appended to the key and the value being the embedding.
        """
        pass

    def _store_embedding(self, user_id, embedding_dict) -> None:
        pass

