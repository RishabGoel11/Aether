from app.core.prompt_builder import PromptBuilder
from app.core.session import Session
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, Role
from app.logger.logger import get_logger

logger = get_logger(__name__)


class ConversationEngine:
    """
    The central orchestrator for user conversations.

    It receives user input, prepares messages for the LLM,
    and returns the generated response.
    """

    def __init__(
        self,
        llm: BaseLLM,
        session: Session,
    ):
        self.llm = llm
        self.session = session

    def chat(self, user_input: str) -> LLMResponse:
        logger.info("Processing user message.")

        message = Message(
            role=Role.USER,
            content=user_input,
        )
        self.session.add_message(message)

        messages = self.session.get_messages()
        prompt = PromptBuilder.build(messages)

        response = self.llm.generate(prompt)

        assistant_message = Message(
            role=Role.ASSISTANT,
            content=response.content,
        )
        self.session.add_message(assistant_message)

        logger.info("Response generated successfully.")

        return response