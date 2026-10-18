"""
Request and response models for the Aether Production REST API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for conversational interaction."""

    message: str = Field(..., min_length=1, description="User prompt or inquiry.")


class ChatResponse(BaseModel):
    """Response containing assistant reply and session status."""

    response: str
    success: bool = True
    error: str | None = None


class RunRequest(BaseModel):
    """Payload for executing an autonomous ReAct agent loop."""

    goal: str = Field(..., min_length=1, description="Goal for the agent to achieve.")
    max_steps: int = Field(default=15, ge=1, le=50, description="Step budget.")


class RunResponse(BaseModel):
    """Response returned from autonomous agent execution."""

    goal: str
    answer: str
    success: bool
    step_count: int
    trace: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class TeamRequest(BaseModel):
    """Payload for multi-agent collaborative task execution."""

    goal: str = Field(..., min_length=1, description="High-level goal for the agent team.")


class TeamResponse(BaseModel):
    """Response containing multi-agent team outputs and final synthesis."""

    goal: str
    final_answer: str
    success: bool
    plan_markdown: str | None = None
    subtasks: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class IndexRequest(BaseModel):
    """Payload for indexing a file or directory into RAG."""

    path: str = Field(..., description="File or directory path to index.")
    recursive: bool = Field(default=True, description="Scan directories recursively.")


class IndexResponse(BaseModel):
    """Response summarizing RAG document ingestion."""

    path: str
    indexed_chunks: int
    success: bool
    message: str


class SpeakRequest(BaseModel):
    """Payload for vocalizing text via TTS."""

    text: str = Field(..., min_length=1, description="Text to speak aloud.")


class SpeakResponse(BaseModel):
    """Response acknowledging vocalization."""

    text: str
    success: bool


class HealthResponse(BaseModel):
    """System health check and diagnostic status."""

    status: str = "ok"
    version: str = "0.11.0"
    ollama_connected: bool = True
    tools_registered: int = 11
