from __future__ import annotations

from uuid import UUID

from app.memory.models import MemoryRecord
from app.memory.stores.base import BaseMemoryStore


class MemoryManager:
    """Coordinates long-term memory operations."""

    def __init__(self, store: BaseMemoryStore) -> None:
        self._store = store

    def remember(self, record: MemoryRecord) -> MemoryRecord:
        """Store a new memory."""

        if not record.content.strip():
            raise ValueError("Memory content cannot be empty.")

        return self._store.add(record)

    def forget(self, memory_id: UUID) -> None:
        """Remove a memory."""

        self._store.delete(memory_id)

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory by its ID."""

        return self._store.get(memory_id)

    def list(self) -> list[MemoryRecord]:
        """Return all stored memories."""

        return self._store.list()   