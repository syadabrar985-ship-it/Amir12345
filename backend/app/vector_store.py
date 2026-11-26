
import json
from pathlib import Path

import faiss
import numpy as np


class FAISSVectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []

    def add_documents(self, chunks: list, embeddings):
        """
        Add document embeddings to FAISS.
        """

        if not chunks:
            raise ValueError("No chunks provided.")

        embeddings = np.asarray(
            embeddings, dtype="float32"
        )

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch.")

        if not np.isfinite(embeddings).all():
            raise ValueError("Embeddings contain invalid values.")

        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)

        if self.index.d != embeddings.shape[1]:
            raise ValueError("Embedding dimensions do not match.")

        self.index.add(embeddings)
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k: int = 4) -> list:
        """
        Search for the most relevant chunks.
        """

        if self.index is None or self.index.ntotal == 0:
            raise ValueError("FAISS index is empty.")

        query_embedding = np.asarray(
            query_embedding, dtype="float32"
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.shape[1] != self.index.d:
            raise ValueError("Query embedding dimension mismatch.")

        if not np.isfinite(query_embedding).all():
            raise ValueError("Query embedding contains invalid values.")

        top_k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(
            query_embedding, top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            results.append({
                "score": float(score),
                "chunk": self.chunks[index]
            })

        return results

    def save(self, directory: str):
        """
        Save FAISS index and chunk metadata.
        """

        if self.index is None:
            raise ValueError("Nothing to save.")

        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(path / "index.faiss")
        )

        with open(
            path / "chunks.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.chunks,
                file,
                ensure_ascii=False,
                indent=2
            )

    def load(self, directory: str):
        """
        Load saved FAISS index and chunk metadata.
        """

        path = Path(directory)

        index_path = path / "index.faiss"
        chunks_path = path / "chunks.json"

        if not index_path.exists():
            raise FileNotFoundError("FAISS index not found.")

        if not chunks_path.exists():
            raise FileNotFoundError("Chunk metadata not found.")

        self.index = faiss.read_index(str(index_path))

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.chunks = json.load(file)

        if self.index.ntotal != len(self.chunks):
            raise ValueError("FAISS index and metadata mismatch.")

        return self
