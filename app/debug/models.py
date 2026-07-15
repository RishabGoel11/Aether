from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DebugEvent(BaseModel):
    """
    Represents a single event that occurred during execution.
    """

    timestamp: datetime = Field(default_factory=datetime.now)
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DebugInfo(BaseModel):
    """
    Collects diagnostic information for a single request.
    """

    provider: str | None = None
    model: str | None = None

    response_time_ms: float | None = None

    message_count: int = 0
    prompt_length: int = 0

    events: list[DebugEvent] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)
