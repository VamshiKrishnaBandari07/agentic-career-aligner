from typing import Protocol


class Embedder(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
