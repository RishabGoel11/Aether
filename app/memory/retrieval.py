from __future__ import annotations

from app.memory.manager import MemoryManager
from app.memory.models import MemoryRecord


class MemoryRetriever:
    """Retrieves memories relevant to the current conversation."""

    def __init__(
        self,
        manager: MemoryManager,
        limit: int = 5,
    ) -> None:
        self._manager = manager
        self._limit = limit

    def _score(
        self,
        query: str,
        memory: MemoryRecord,
    ) -> int:
        """
        Score a memory based on keyword overlap with the query.

        Version 1 performs a simple case-insensitive token overlap.
        """

        query_tokens = set(query.lower().split())
        memory_tokens = set(memory.content.lower().split())

        return len(query_tokens & memory_tokens)

    def retrieve(
        self,
        query: str,
    ) -> list[MemoryRecord]:
        """
        Retrieve memories relevant to the given query.

        Version 1:
        - Scores memories using keyword overlap.
        - Returns the highest-ranked memories.
        """

        memories = self._manager.list()

        ranked = sorted(
            memories,
            key=lambda memory: self._score(query, memory),
            reverse=True,
        )

        return ranked[: self._limit]