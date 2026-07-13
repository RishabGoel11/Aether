from app.core.prompt_builder import PromptBuilder
from app.core.session import Session
from app.debug.collector import DebugCollector
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
        self.debug_collector: DebugCollector | None = None

    def chat(self, user_input: str) -> LLMResponse:
        # Create a fresh collector for this request.
        self.debug_collector = DebugCollector()
        self.debug_collector.start()
        self.debug_collector.add_event("Conversation started")

        try:
            logger.info("Processing user message.")

            message = Message(
                role=Role.USER,
                content=user_input,
            )
            self.session.add_message(message)

            self.debug_collector.add_event(
                "User message added",
            )

            messages = self.session.get_messages()
            prompt = PromptBuilder.build(messages)

            self.debug_collector.set_message_count(len(prompt))
            self.debug_collector.set_prompt_length(
                sum(len(message.content) for message in prompt)
            )

            self.debug_collector.add_event(
                "Prompt built",
            )

            self.debug_collector.add_event(
                "LLM request started",
            )

            response = self.llm.generate(prompt)

            self.debug_collector.add_event(
                "LLM response received",
            )

            assistant_message = Message(
                role=Role.ASSISTANT,
                content=response.content,
            )
            self.session.add_message(assistant_message)

            self.debug_collector.add_event(
                "Assistant message stored",
            )

            logger.info("Response generated successfully.")

            return response

        finally:
            self.debug_collector.finish()