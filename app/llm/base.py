from abc import ABC, abstractmethod

from app.llm.models import LLMResponse, Message


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, messages: list[Message]) -> LLMResponse:
        """
        Generate a response from the provided conversation messages.
        """
        pass
