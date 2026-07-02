import numpy as np

from job_matcher.core.config import Settings
from job_matcher.integrations.openai.client import create_openai_client
from job_matcher.integrations.openai.embeddings import OpenAIEmbeddings
from job_matcher.utils.chunking import chunk_text


class OpenAIEmbedder:
    def __init__(self, settings: Settings) -> None:
        client = create_openai_client(settings)
        self._embeddings = OpenAIEmbeddings(client, settings)
        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self._embeddings.create(texts)

    async def embed_document(self, text: str) -> list[float]:
        chunks = chunk_text(text, self._chunk_size, self._chunk_overlap)
        vectors = await self.embed_texts(chunks)
        if not vectors:
            return []
        matrix = np.array(vectors, dtype=float)
        mean_vector = matrix.mean(axis=0)
        norm = np.linalg.norm(mean_vector)
        if norm == 0:
            return mean_vector.tolist()
        return (mean_vector / norm).tolist()
