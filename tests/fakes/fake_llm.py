from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message


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

    def generate(self, messages: list[Message]) -> LLMResponse:
        self.call_count += 1
        self.received_messages.append(messages)

        if self.exception is not None:
            raise self.exception

        return LLMResponse(content=self.response)

    def reset(self) -> None:
        """Reset recorded interactions."""
        self.call_count = 0
        self.received_messages.clear()
