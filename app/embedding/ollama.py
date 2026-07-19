from __future__ import annotations

from ollama import Client

from app.embedding.base import BaseEmbedder


class OllamaEmbedder(BaseEmbedder):
    """Embedding provider backed by Ollama."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        host: str = "http://localhost:11434",
    ) -> None:
        self._client = Client(host=host)
        self._model = model

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding for a single text."""

        response = self._client.embed(
            model=self._model,
            input=text,
        )

        return response.embeddings[0]

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        response = self._client.embed(
            model=self._model,
            input=texts,
        )

        return response.embeddings