"""Sentence embedding service using Sentence Transformers."""

from typing import List, Optional

import numpy as np

from resume_analyzer.config.settings import Settings, get_settings
from resume_analyzer.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings for resume and job description text."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize embedding service.

        Args:
            settings: Application settings.
        """
        self._settings = settings or get_settings()
        self._model = None

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a single text into embedding vector.

        Args:
            text: Input text.

        Returns:
            Numpy embedding array.
        """
        model = self._get_model()
        if model is None:
            return self._fallback_embedding(text)
        embedding = model.encode(text, convert_to_numpy=True)
        return np.asarray(embedding, dtype=np.float32)

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts.

        Args:
            texts: List of strings.

        Returns:
            2D numpy array of embeddings.
        """
        model = self._get_model()
        if model is None:
            return np.vstack([self._fallback_embedding(t) for t in texts])
        return np.asarray(model.encode(texts, convert_to_numpy=True), dtype=np.float32)

    def _get_model(self):
        """Lazy-load SentenceTransformer model."""
        if self._model is not None:
            return self._model if self._model is not False else None
        try:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: %s", self._settings.embedding_model)
            self._model = SentenceTransformer(self._settings.embedding_model)
        except Exception as exc:
            logger.warning("Embedding model unavailable (%s). Using fallback.", exc)
            self._model = False
        return self._model if self._model is not False else None

    def _fallback_embedding(self, text: str, dim: int = 384) -> np.ndarray:
        """
        Simple bag-of-words style hash embedding when model unavailable.

        Args:
            text: Input text.
            dim: Vector dimension.

        Returns:
            Normalized pseudo-embedding.
        """
        vec = np.zeros(dim, dtype=np.float32)
        for i, token in enumerate(text.lower().split()):
            idx = hash(token) % dim
            vec[idx] += 1.0 / (i + 1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec
