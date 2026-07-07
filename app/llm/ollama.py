import ollama

from app.config.config import LLMSettings
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message


class OllamaLLM(BaseLLM):
    def __init__(self, settings: LLMSettings):
        self.model = settings.model
        self.temperature = settings.temperature

    def generate(self, messages: list[Message]) -> LLMResponse:
        ollama_messages = []

        for message in messages:
            ollama_messages.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        response = ollama.chat(
            model=self.model,
            messages=ollama_messages,
        )

        return LLMResponse(
            content=response["message"]["content"]
        )