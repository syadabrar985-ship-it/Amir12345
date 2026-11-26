import json
import faiss
import numpy as np

from app.config import FAISS_INDEX_PATH, METADATA_PATH
from app.embeddings import create_embeddings


def save_vector_store(texts: list[str], metadata: list[dict]):
    if not texts:
        raise ValueError("No text chunks were provided.")

    embeddings = create_embeddings(texts)
    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(FAISS_INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)

    return len(texts)


def load_vector_store():
    if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
        return None, []

    index = faiss.read_index(str(FAISS_INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return index, metadata


def search_vectors(query: str, top_k: int = 4):
    index, metadata = load_vector_store()

    if index is None or not metadata:
        return []

    query_embedding = create_embeddings([query])
    query_embedding = np.asarray(query_embedding, dtype="float32")

    scores, indices = index.search(
        query_embedding,
        min(top_k, index.ntotal)
    )

    results = []

    for score, position in zip(scores[0], indices[0]):
        if position < 0:
            continue

        item = metadata[position].copy()
        item["score"] = float(score)
        results.append(item)

    return results
