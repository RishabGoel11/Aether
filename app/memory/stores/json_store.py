from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.memory.models import MemoryRecord
from app.memory.stores.base import BaseMemoryStore


class JsonMemoryStore(BaseMemoryStore):
    """JSON-backed implementation of the memory store."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        self._records: dict[UUID, MemoryRecord] = {}

        self.load()

    def load(self) -> None:
        """Load memories from the JSON file."""

        if not self.filepath.exists():
            self._records = {}
            return

        with self.filepath.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self._records = {
            record.id: record
            for record in (MemoryRecord.model_validate(item) for item in data)
        }

    def save(self) -> None:
        """Persist all memories to the JSON file."""

        with self.filepath.open("w", encoding="utf-8") as file:
            json.dump(
                [
                    record.model_dump(mode="json")
                    for record in self._records.values()
                ],
                file,
                indent=4,
            )

    def add(self, record: MemoryRecord) -> MemoryRecord:
        """Add a new memory."""

        self._records[record.id] = record
        self.save()

        return record

    def update(self, record: MemoryRecord) -> MemoryRecord:
        """Update an existing memory."""

        if record.id not in self._records:
            raise ValueError(f"Memory '{record.id}' does not exist.")

        self._records[record.id] = record
        self.save()

        return record

    def delete(self, memory_id: UUID) -> None:
        """Delete a memory."""

        if memory_id not in self._records:
            raise ValueError(f"Memory '{memory_id}' does not exist.")

        del self._records[memory_id]
        self.save()

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory by ID."""

        return self._records.get(memory_id)

    def list(self) -> list[MemoryRecord]:
        """Return a copy of all memories."""

        return list(self._records.values())