from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message
from app.tools.models import ToolDefinition


class FakeLLM(BaseLLM):
    """
    Test double for BaseLLM.

    Provides deterministic responses and records interactions
    for use in unit and integration tests.
    """

    def __init__(
        self,
        response: str = "Fake response",
        exception: Exception | None = None,
    ) -> None:
        self.response = response
        self.exception = exception

        self.call_count = 0
        self.received_messages: list[list[Message]] = []
        self.received_tools: list[list[ToolDefinition] | None] = []

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        self.call_count += 1
        self.received_messages.append(messages)
        self.received_tools.append(tools)

        if self.exception is not None:
            raise self.exception

        return LLMResponse(content=self.response)

    def reset(self) -> None:
        """Reset recorded interactions."""
        self.call_count = 0
        self.received_messages.clear()
        self.received_tools.clear()
