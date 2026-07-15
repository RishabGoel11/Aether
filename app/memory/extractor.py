from __future__ import annotations

from app.memory.models import (
    MemoryCategory,
    MemoryRecord,
    MemorySource,
)


class MemoryExtractor:
    """
    Extracts long-term memories from user messages.

    Version 1 uses simple rule-based extraction.
    Future versions may use LLMs or other AI techniques.
    """

    MEMORY_PATTERNS: tuple[tuple[str, MemoryCategory], ...] = (
        ("my favorite", MemoryCategory.PREFERENCE),
        ("i prefer", MemoryCategory.PREFERENCE),
        ("i'm building", MemoryCategory.PROJECT),
        ("i am building", MemoryCategory.PROJECT),
        ("i'm working on", MemoryCategory.PROJECT),
        ("i am working on", MemoryCategory.PROJECT),
    )

    def extract(
        self,
        message: str,
    ) -> list[MemoryRecord]:
        """
        Extract memories from a user message.

        Version 1:
        - Rule-based matching.
        - Returns zero or more memories.
        """

        text = message.lower()

        memories: list[MemoryRecord] = []

        for pattern, category in self.MEMORY_PATTERNS:
            if pattern in text:
                memories.append(
                    MemoryRecord(
                        content=message,
                        category=category,
                        source=MemorySource.AUTOMATIC,
                    )
                )

        return memories
