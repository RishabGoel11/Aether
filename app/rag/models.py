from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    """Represents an ingested raw document."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    """Represents a passage extracted from a Document."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    chunk_index: int = 0
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Represents a retrieved chunk with its similarity score."""

    model_config = ConfigDict(validate_assignment=True)

    chunk: Chunk
    score: float = 0.0
