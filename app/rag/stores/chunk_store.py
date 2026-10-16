from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.rag.models import Chunk


class BaseChunkStore(ABC):
    """Abstract interface for storing and retrieving document chunks."""

    @abstractmethod
    def add(self, chunk: Chunk) -> Chunk:
        """Add a single chunk to the store."""

    @abstractmethod
    def add_many(self, chunks: list[Chunk]) -> list[Chunk]:
        """Add multiple chunks to the store."""

    @abstractmethod
    def get(self, chunk_id: UUID) -> Chunk | None:
        """Retrieve a chunk by ID."""

    @abstractmethod
    def list(self) -> list[Chunk]:
        """List all chunks in the store."""

    @abstractmethod
    def delete(self, chunk_id: UUID) -> None:
        """Delete a chunk by ID."""

    @abstractmethod
    def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks belonging to a document ID."""

    @abstractmethod
    def delete_by_source(self, source: str) -> None:
        """Delete all chunks originating from a source path."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all chunks from the store."""


class InMemoryChunkStore(BaseChunkStore):
    """In-memory chunk store implementation."""

    def __init__(self) -> None:
        self._chunks: dict[UUID, Chunk] = {}

    def add(self, chunk: Chunk) -> Chunk:
        self._chunks[chunk.id] = chunk
        return chunk

    def add_many(self, chunks: list[Chunk]) -> list[Chunk]:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
        return chunks

    def get(self, chunk_id: UUID) -> Chunk | None:
        return self._chunks.get(chunk_id)

    def list(self) -> list[Chunk]:
        return list(self._chunks.values())

    def delete(self, chunk_id: UUID) -> None:
        self._chunks.pop(chunk_id, None)

    def delete_by_document(self, document_id: UUID) -> None:
        to_delete = [cid for cid, chunk in self._chunks.items() if chunk.document_id == document_id]
        for cid in to_delete:
            del self._chunks[cid]

    def delete_by_source(self, source: str) -> None:
        to_delete = [cid for cid, chunk in self._chunks.items() if chunk.source == source]
        for cid in to_delete:
            del self._chunks[cid]

    def clear(self) -> None:
        self._chunks.clear()
