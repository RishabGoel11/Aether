from __future__ import annotations

from uuid import UUID

from app.embedding.base import BaseEmbedder
from app.memory.models import MemoryCategory, MemoryRecord
from app.memory.stores.base import BaseMemoryStore
from app.vectorstore.base import BaseVectorStore


class MemoryManager:
    """Coordinates long-term memory operations."""

    def __init__(
        self,
        store: BaseMemoryStore,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,
    ) -> None:
        self._store = store
        self._embedder = embedder
        self._vector_store = vector_store

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

        stored = self._store.add(record)

        embedding = self._embedder.embed(stored.content)

        self._vector_store.add(
            stored.id,
            embedding,
        )

        return stored

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

        self._vector_store.delete(memory_id)

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

        return [memory for memory in self._store.list() if memory.category == category]

    def search_content(
        self,
        query: str,
    ) -> list[MemoryRecord]:
        """
        Search memories by content.

        Version 1 performs a case-insensitive substring search.
        """

        query = query.lower()

        return [memory for memory in self._store.list() if query in memory.content.lower()]

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[MemoryRecord]:
        """
        Search memories using semantic similarity.
        """

        embedding = self._embedder.embed(query)

        memory_ids = self._vector_store.search(
            embedding,
            limit=limit,
        )

        memories: list[MemoryRecord] = []

        for memory_id in memory_ids:
            memory = self._store.get(memory_id)

            if memory is not None:
                memories.append(memory)

        return memories

    def update(
        self,
        record: MemoryRecord,
    ) -> MemoryRecord:
        """
        Update an existing memory.
        """

        if not record.content.strip():
            raise ValueError("Memory content cannot be empty.")

        updated = self._store.update(record)

        embedding = self._embedder.embed(updated.content)

        self._vector_store.update(
        updated.id,
        embedding,
        )

        return updated
