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

    def retrieve(self, query: str) -> list[MemoryRecord]:
        """
        Retrieve memories relevant to the given query.

        Version 1:
        - Ignores the query.
        - Returns the first `limit` memories.
        """

        memories = self._manager.list()

        return memories[: self._limit]
