"""Cosine similarity calculations for embeddings (scikit-learn)."""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine


class SimilarityService:
    """Compute similarity between text embeddings using scikit-learn."""

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec_a: First embedding.
            vec_b: Second embedding.

        Returns:
            Similarity score between 0 and 1.
        """
        a = np.asarray(vec_a, dtype=np.float64).flatten().reshape(1, -1)
        b = np.asarray(vec_b, dtype=np.float64).flatten().reshape(1, -1)
        if a.size == 0 or b.size == 0:
            return 0.0
        score = float(sklearn_cosine(a, b)[0][0])
        return max(0.0, min(1.0, score))

    def match_percentage(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Return match score as percentage 0-100.

        Args:
            vec_a: First embedding.
            vec_b: Second embedding.

        Returns:
            Percentage score.
        """
        return round(self.cosine_similarity(vec_a, vec_b) * 100, 1)
