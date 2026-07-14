from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryCategory(str, Enum):
    PROFILE = "profile"
    PREFERENCE = "preference"
    PROJECT = "project"
    SKILL = "skill"
    GOAL = "goal"
    OTHER = "other"


class MemorySource(str, Enum):
    EXPLICIT = "explicit"
    AUTOMATIC = "automatic"


class MemoryRecord(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    content: str
    category: MemoryCategory = MemoryCategory.OTHER
    source: MemorySource = MemorySource.AUTOMATIC
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))