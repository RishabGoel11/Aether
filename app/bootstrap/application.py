from app.config.config import Settings
from app.core.engine import ConversationEngine
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.session.manager import SessionManager
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class Application:
    """
    Represents a running Aether application.

    This class owns the application's core components and
    provides the primary interface for interacting with them.
    """

    def __init__(
        self,
        settings: Settings,
        engine: ConversationEngine,
        session: SessionManager,
        memory: MemoryManager,
        extractor: MemoryExtractor,
        tools: ToolRegistry,
        tool_executor: ToolExecutor,
    ):
        self.settings = settings
        self.engine = engine
        self.session = session
        self.memory = memory
        self.extractor = extractor
        self.tools = tools
        self.tool_executor = tool_executor

    def chat(self, user_input: str):
        """
        Send a message to Aether.
        """
        response = self.engine.chat(user_input)

        messages = self.engine.session.get_messages()

        memories = self.extractor.extract(messages)

        self.memory.add_all(memories)

        self.session.save(self.engine.session)

        return response

    def clear_conversation(self) -> None:
        """
        Clear the current conversation and start a new session.
        """
        self.engine.session = self.session.clear()