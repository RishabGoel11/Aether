from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class BaseVectorStore(ABC):
    """Abstract interface for vector stores."""

    @abstractmethod
    def add(
        self,
        memory_id: UUID,
        embedding: list[float],
    ) -> None:
        """Store an embedding."""

    @abstractmethod
    def update(
        self,
        memory_id: UUID,
        embedding: list[float],
    ) -> None:
        """Update an existing embedding."""

    @abstractmethod
    def delete(
        self,
        memory_id: UUID,
    ) -> None:
        """Delete an embedding."""

    @abstractmethod
    def get(
        self,
        memory_id: UUID,
    ) -> list[float] | None:
        """Retrieve an embedding."""

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[str]:
        """Return the keys of the nearest embeddings."""
