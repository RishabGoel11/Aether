from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.rag.models import Chunk
from app.rag.stores.chunk_store import BaseChunkStore


class JsonChunkStore(BaseChunkStore):
    """JSON-backed persistent implementation of BaseChunkStore."""

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._chunks: dict[UUID, Chunk] = {}
        self.load()

    def load(self) -> None:
        """Load stored chunks from the JSON file."""
        if not self.filepath.exists():
            self._chunks = {}
            return

        with self.filepath.open("r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                self._chunks = {}
                return

        self._chunks = {chunk.id: chunk for chunk in (Chunk.model_validate(item) for item in data)}

    def save(self) -> None:
        """Persist all stored chunks to the JSON file."""
        with self.filepath.open("w", encoding="utf-8") as file:
            json.dump(
                [chunk.model_dump(mode="json") for chunk in self._chunks.values()],
                file,
                indent=2,
            )

    def add(self, chunk: Chunk) -> Chunk:
        self._chunks[chunk.id] = chunk
        self.save()
        return chunk

    def add_many(self, chunks: list[Chunk]) -> list[Chunk]:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
        self.save()
        return chunks

    def get(self, chunk_id: UUID) -> Chunk | None:
        return self._chunks.get(chunk_id)

    def list(self) -> list[Chunk]:
        return list(self._chunks.values())

    def delete(self, chunk_id: UUID) -> None:
        if chunk_id in self._chunks:
            del self._chunks[chunk_id]
            self.save()

    def delete_by_document(self, document_id: UUID) -> None:
        to_delete = [cid for cid, chunk in self._chunks.items() if chunk.document_id == document_id]
        for cid in to_delete:
            del self._chunks[cid]
        if to_delete:
            self.save()

    def delete_by_source(self, source: str) -> None:
        to_delete = [cid for cid, chunk in self._chunks.items() if chunk.source == source]
        for cid in to_delete:
            del self._chunks[cid]
        if to_delete:
            self.save()

    def clear(self) -> None:
        self._chunks.clear()
        self.save()
