"""Embedding model using OpenAI text-embedding-3-small (no torch required)."""

import logging
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)

# OpenAI embeddings have 1536 dimensions by default for text-embedding-3-small
DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_DIMENSION = 1536
BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per call


class EmbeddingModel:
    """Wraps OpenAI embeddings API for encoding text into dense vectors."""

    def __init__(self, model_name: str = DEFAULT_MODEL, api_key: str | None = None):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)
        self.dimension = DEFAULT_DIMENSION

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into embeddings. Returns float32 numpy array."""
        all_embeddings = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            # Truncate any super-long texts to avoid token limits
            batch = [t[:8000] for t in batch]

            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch,
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return np.array(all_embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query string."""
        return self.encode([query])
