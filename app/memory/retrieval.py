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

    def retrieve(
        self,
        query: str,
    ) -> list[MemoryRecord]:
        """
        Retrieve memories using semantic similarity.
        """

        return self._manager.semantic_search(
            query=query,
            limit=self._limit,
        )