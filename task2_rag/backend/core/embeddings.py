"""Embedding model wrapper using sentence-transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Wraps sentence-transformers for encoding text into dense vectors."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into embeddings. Returns float32 numpy array."""
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query string."""
        return self.encode([query])
