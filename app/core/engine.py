from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, Role


class ConversationEngine:
    """
    The central orchestrator for user conversations.

    It receives user input, prepares messages for the LLM,
    and returns the generated response.
    """

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def chat(self, user_input: str) -> LLMResponse:
        messages = [
            Message(
                role=Role.USER,
                content=user_input,
            )
        ]

        return self.llm.generate(messages)