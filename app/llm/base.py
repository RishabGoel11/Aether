from abc import ABC, abstractmethod

from app.llm.models import LLMResponse, Message
from app.tools.models import ToolDefinition


class BaseLLM(ABC):
    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        """
        Generate a response from the provided conversation messages.

        Tools describe capabilities available to the language model.
        """
        pass
