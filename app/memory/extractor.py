from __future__ import annotations

from app.llm.models import Message, Role
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
        messages: list[Message],
    ) -> list[MemoryRecord]:
        """
        Extract memories from the latest user message in a conversation.

        Version 2:
        - Accepts conversation messages.
        - Applies rule-based extraction to the latest user message.
        - Returns zero or more memories.
        """

        latest_user_message = next(
            (
                message
                for message in reversed(messages)
                if message.role == Role.USER
            ),
            None,
        )

        if latest_user_message is None:
            return []

        text = latest_user_message.content.lower()

        memories: list[MemoryRecord] = []

        for pattern, category in self.MEMORY_PATTERNS:
            if pattern in text:
                memories.append(
                    MemoryRecord(
                        content=latest_user_message.content,
                        category=category,
                        source=MemorySource.AUTOMATIC,
                    )
                )

        return memories