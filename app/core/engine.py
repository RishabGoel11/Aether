from app.core.prompt_builder import PromptBuilder
from app.core.session import Session
from app.debug.collector import DebugCollector
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, Role
from app.logger.logger import get_logger
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)


class ConversationEngine:
    """
    The central orchestrator for user conversations.

    It receives user input, extracts long-term memories,
    prepares messages for the LLM, executes requested tools,
    and returns the generated response.
    """

    def __init__(
        self,
        llm: BaseLLM,
        session: Session,
        memory_retriever: MemoryRetriever,
        memory_extractor: MemoryExtractor,
        memory_manager: MemoryManager,
        tools: ToolRegistry,
        tool_executor: ToolExecutor,
        tool_policy: ToolPolicy,
        max_tool_rounds: int = 5,
    ):
        self.llm = llm
        self.session = session
        self.memory_retriever = memory_retriever
        self.memory_extractor = memory_extractor
        self.memory_manager = memory_manager
        self.tools = tools
        self.tool_executor = tool_executor
        self.tool_policy = tool_policy
        if max_tool_rounds < 1:
            raise ValueError("max_tool_rounds must be at least 1.")

        self.max_tool_rounds = max_tool_rounds
        self.debug_collector: DebugCollector | None = None

    def _execute_tool_calls(
        self,
        response: LLMResponse,
    ) -> list[Message]:
        """Execute requested tools and return their results as messages."""
        tool_messages = []

        for tool_call in response.tool_calls:
            self.debug_collector.add_event(
                f"Tool requested: {tool_call.name}",
            )

            try:
                tool = self.tools.get(tool_call.name)

                if not self.tool_policy.is_allowed(tool.definition()):
                    result_content = f"Tool execution denied by policy: {tool_call.name}"
                else:
                    result = self.tool_executor.execute(
                        tool,
                        tool_call.arguments,
                    )

                    if result.success:
                        result_content = str(result.output)
                    else:
                        result_content = f"Tool execution failed: {result.error}"

            except Exception as exc:
                logger.error(
                    "Failed to execute tool '%s'.",
                    tool_call.name,
                    exc_info=True,
                )

                result_content = f"Tool execution failed: {exc}"

            tool_message = Message(
                role=Role.TOOL,
                content=(f"Tool result for '{tool_call.name}': {result_content}"),
            )

            tool_messages.append(tool_message)
            self.session.add_message(tool_message)

            self.debug_collector.add_event(
                f"Tool completed: {tool_call.name}",
            )

        return tool_messages

    def chat(self, user_input: str) -> LLMResponse:
        # Create a fresh collector for this request.
        self.debug_collector = DebugCollector()
        self.debug_collector.start()
        self.debug_collector.add_event("Conversation started")

        try:
            logger.info("Processing user message.")

            user_message = Message(
                role=Role.USER,
                content=user_input,
            )
            self.session.add_message(user_message)

            self.debug_collector.add_event(
                "User message added",
            )

            messages = self.session.get_messages()

            extracted_memories = self.memory_extractor.extract(messages)

            for memory in extracted_memories:
                self.memory_manager.remember(memory)

            self.debug_collector.add_event(
                f"Extracted {len(extracted_memories)} memories",
            )

            memories = self.memory_retriever.retrieve(user_input)

            self.debug_collector.add_event(
                f"Retrieved {len(memories)} memories",
            )

            prompt = PromptBuilder.build(
                messages,
                memories,
            )

            self.debug_collector.set_message_count(len(prompt))
            self.debug_collector.set_prompt_length(
                sum(len(message.content) for message in prompt),
            )

            self.debug_collector.add_event(
                "Prompt built",
            )

            tool_definitions = [tool.definition() for tool in self.tools.list()]

            self.debug_collector.add_event(
                f"Provided {len(tool_definitions)} tools",
            )

            self.debug_collector.add_event(
                "LLM request started",
            )

            response = self.llm.generate(
                prompt,
                tools=tool_definitions,
            )

            self.debug_collector.add_event(
                "LLM response received",
            )

            tool_round = 0

            while response.tool_calls and tool_round < self.max_tool_rounds:
                tool_round += 1

                self.debug_collector.add_event(
                    f"Tool round {tool_round} started",
                )

                tool_messages = self._execute_tool_calls(response)

                prompt.extend(tool_messages)

                self.debug_collector.add_event(
                    f"Sending tool results to LLM (round {tool_round})",
                )

                response = self.llm.generate(
                    prompt,
                    tools=tool_definitions,
                )

                self.debug_collector.add_event(
                    f"Tool round {tool_round} completed",
                )

            if response.tool_calls:
                self.debug_collector.add_event(
                    "Maximum tool rounds reached",
                )
            else:
                self.debug_collector.add_event(
                    "Final LLM response received",
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
