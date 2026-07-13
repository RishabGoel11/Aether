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


class ToolSettings(BaseModel):
    enabled: bool = True

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
    tools: ToolSettings = Field(default_factory=ToolSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    debug: DebugSettings = Field(default_factory=DebugSettings)
