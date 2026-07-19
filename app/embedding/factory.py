from __future__ import annotations

from app.embedding.base import BaseEmbedder
from app.embedding.ollama import OllamaEmbedder


class EmbeddingFactory:
    """Factory for creating embedding providers."""

    @staticmethod
    def create() -> BaseEmbedder:
        return OllamaEmbedder()