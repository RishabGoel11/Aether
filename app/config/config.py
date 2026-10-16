from enum import Enum

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    OLLAMA = "ollama"


class LLMSettings(BaseModel):
    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = Field(default="qwen3:8b")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )


class MemorySettings(BaseModel):
    enabled: bool = True


class SessionSettings(BaseModel):
    """
    Configuration for session and conversation history management.
    """

    history_window: int = Field(
        default=20,
        ge=4,
        description=(
            "Maximum number of recent messages sent to the LLM. "
            "Prevents context overflow with long conversations."
        ),
    )


class ToolSettings(BaseModel):
    enabled: bool = True


class RAGSettings(BaseModel):
    """
    Configuration for Retrieval-Augmented Generation (RAG).
    """

    enabled: bool = True
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=100, ge=0)
    retrieval_limit: int = Field(default=3, gt=0)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)


class DebugSettings(BaseModel):
    """
    Configuration for Aether's debugging infrastructure.
    """

    enabled: bool = False


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingSettings(BaseModel):
    level: LogLevel = LogLevel.INFO


class Settings(BaseModel):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    session: SessionSettings = Field(default_factory=SessionSettings)
    tools: ToolSettings = Field(default_factory=ToolSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    debug: DebugSettings = Field(default_factory=DebugSettings)
