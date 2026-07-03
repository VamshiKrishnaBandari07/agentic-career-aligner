import re

import numpy as np

from job_matcher.utils.chunking import chunk_text


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.]+", text.lower())


class LocalEmbedder:
    """Hash-based bag-of-words embedder — no external API required."""

    def __init__(self, dimensions: int = 512) -> None:
        self._dimensions = dimensions

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    async def embed_document(self, text: str) -> list[float]:
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        vectors = await self.embed_texts(chunks)
        if not vectors:
            return []
        matrix = np.array(vectors, dtype=float)
        mean_vector = matrix.mean(axis=0)
        norm = np.linalg.norm(mean_vector)
        if norm == 0:
            return mean_vector.tolist()
        return (mean_vector / norm).tolist()

    def _embed_one(self, text: str) -> list[float]:
        vector = np.zeros(self._dimensions, dtype=float)
        for token in _tokenize(text):
            vector[hash(token) % self._dimensions] += 1.0
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector.tolist()
        return (vector / norm).tolist()
