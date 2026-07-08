from enum import Enum

from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    provider: str = Field(default="ollama")
    model: str = Field(default="qwen3:8b")
    temperature: float = Field(default=0.7)


class MemorySettings(BaseModel):
    enabled: bool = True


class ToolSettings(BaseModel):
    enabled: bool = True


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
