from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ToolCall(BaseModel):
    """A request from the LLM to execute a tool."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    """Response returned by an LLM provider."""

    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
