from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL


_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)

    return _model


def create_embeddings(texts: list[str]):
    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings
