from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """Abstract interface for embedding providers."""

    @abstractmethod
    def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding for a single text."""

    @abstractmethod
    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""