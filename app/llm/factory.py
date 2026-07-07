from app.config.config import LLMSettings
from app.llm.base import BaseLLM
from app.llm.ollama import OllamaLLM


class LLMFactory:
    @staticmethod
    def create(settings: LLMSettings) -> BaseLLM:
        if settings.provider == "ollama":
            return OllamaLLM(settings)

        raise ValueError(
            f"Unsupported LLM provider: {settings.provider}"
        )