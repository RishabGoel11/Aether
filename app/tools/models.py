from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Serializable description of a tool."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    input_schema: dict[str, Any]


class ToolResult(BaseModel):
    """Standard result returned by a tool execution."""

    success: bool
    output: Any = None
    error: str | None = None
