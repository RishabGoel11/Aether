from __future__ import annotations

from uuid import UUID

from app.memory.models import MemoryCategory, MemoryRecord
from app.memory.stores.base import BaseMemoryStore


class MemoryManager:
    """Coordinates long-term memory operations."""

    def __init__(self, store: BaseMemoryStore) -> None:
        self._store = store

    def remember(
        self,
        record: MemoryRecord,
    ) -> MemoryRecord:
        """
        Store a memory if it passes the forgetting strategy.

        Version 1:
        - Reject empty memories.
        - Reject duplicate memory content.
        """

        if not record.content.strip():
            raise ValueError("Memory content cannot be empty.")

        for existing in self._store.list():
            if existing.content.strip().lower() == record.content.strip().lower():
                return existing

        return self._store.add(record)
        
    def add_all(
        self,
        memories: list[MemoryRecord],
    ) -> None:
        """
        Add multiple memories to the store.
        """

        for memory in memories:
            self.remember(memory)

    def forget(self, memory_id: UUID) -> None:
        """Remove a memory."""

        self._store.delete(memory_id)

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory by its ID."""

        return self._store.get(memory_id)

    def list(self) -> list[MemoryRecord]:
        """Return all stored memories."""

        return self._store.list()


    def find_by_category(
        self,
        category: MemoryCategory,
    ) -> list[MemoryRecord]:
        """
        Return all memories belonging to a category.
        """

        return [
            memory
            for memory in self._store.list()
            if memory.category == category
        ]


    def search_content(
        self,
        query: str,
    ) -> list[MemoryRecord]:
        """
        Search memories by content.

        Version 1 performs a case-insensitive substring search.
        """

        query = query.lower()

        return [
            memory
            for memory in self._store.list()
            if query in memory.content.lower()
        ]


    def update(
        self,
        record: MemoryRecord,
    ) -> MemoryRecord:
        """
        Update an existing memory.
        """

        if not record.content.strip():
            raise ValueError("Memory content cannot be empty.")

        return self._store.update(record)