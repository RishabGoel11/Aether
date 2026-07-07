from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    provider: str = Field(default="ollama")
    model: str = Field(default="qwen3:8b")
    temperature: float = Field(default=0.7)


class MemorySettings(BaseModel):
    enabled: bool = True


class ToolSettings(BaseModel):
    enabled: bool = True


class LoggingSettings(BaseModel):
    level: str = "INFO"


class Settings(BaseModel):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    tools: ToolSettings = Field(default_factory=ToolSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
