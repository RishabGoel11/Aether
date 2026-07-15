from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.memory.models import MemoryRecord


class BaseMemoryStore(ABC):
    """Abstract interface for persistent memory storage."""

    @abstractmethod
    def load(self) -> None:
        """Load all memories from persistent storage."""
        ...

    @abstractmethod
    def save(self) -> None:
        """Persist all in-memory memories."""
        ...

    @abstractmethod
    def add(self, record: MemoryRecord) -> MemoryRecord:
        """Add a new memory."""
        ...

    @abstractmethod
    def update(self, record: MemoryRecord) -> MemoryRecord:
        """Update an existing memory."""
        ...

    @abstractmethod
    def delete(self, memory_id: UUID) -> None:
        """Delete a memory by its ID."""
        ...

    @abstractmethod
    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory by its ID."""
        ...

    @abstractmethod
    def list(self) -> list[MemoryRecord]:
        """Return all stored memories."""
        ...
