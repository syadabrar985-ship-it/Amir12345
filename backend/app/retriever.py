
from pathlib import Path

from app.embeddings import EmbeddingModel
from app.vector_store import FAISSVectorStore


VECTOR_DB_PATH = (
    Path(__file__).resolve().parents[1] / "vector_db"
)


class Retriever:

    def __init__(self, vector_db_path=None):

        self.vector_db_path = (
            Path(vector_db_path)
            if vector_db_path
            else VECTOR_DB_PATH
        )

        self.embedding_model = EmbeddingModel()

        self.vector_store = FAISSVectorStore()
        self.vector_store.load(str(self.vector_db_path))

    def retrieve(self, query: str, top_k: int = 4):
        """
        Retrieve relevant document chunks.
        """

        query_embedding = (
            self.embedding_model.create_query_embedding(query)
        )

        results = self.vector_store.search(
            query_embedding,
            top_k
        )

        return results
