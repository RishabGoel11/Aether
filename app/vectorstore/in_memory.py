from __future__ import annotations

import math
from uuid import UUID

from app.vectorstore.base import BaseVectorStore


class InMemoryVectorStore(BaseVectorStore):
    """In-memory implementation of a vector store."""

    def __init__(self) -> None:
        self._vectors: dict[UUID, list[float]] = {}

    def add(
        self,
        memory_id: UUID,
        embedding: list[float],
    ) -> None:
        self._vectors[memory_id] = embedding

    def update(
        self,
        memory_id: UUID,
        embedding: list[float],
    ) -> None:
        if memory_id not in self._vectors:
            raise ValueError(f"Vector '{memory_id}' does not exist.")

        self._vectors[memory_id] = embedding

    def delete(
        self,
        memory_id: UUID,
    ) -> None:
        self._vectors.pop(memory_id, None)

    def get(
        self,
        memory_id: UUID,
    ) -> list[float] | None:
        return self._vectors.get(memory_id)

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[UUID]:
        scored = [
            (
                memory_id,
                self._cosine_similarity(
                    embedding,
                    stored_embedding,
                ),
            )
            for memory_id, stored_embedding in self._vectors.items()
        ]

        scored.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            memory_id
            for memory_id, _ in scored[:limit]
        ]

    @staticmethod
    def _cosine_similarity(
        first: list[float],
        second: list[float],
    ) -> float:
        if len(first) != len(second):
            raise ValueError("Embeddings must have the same dimensions.")

        dot_product = sum(
            x * y
            for x, y in zip(first, second, strict=True)
        )

        first_norm = math.sqrt(sum(x * x for x in first))
        second_norm = math.sqrt(sum(y * y for y in second))

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return dot_product / (first_norm * second_norm)