from app.config.config import Settings
from app.core.engine import ConversationEngine
from app.memory.manager import MemoryManager
from app.session.manager import SessionManager


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
    ):
        self.settings = settings
        self.engine = engine
        self.session = session
        self.memory = memory

    def chat(self, user_input: str):
        """
        Send a message to Aether.
        """
        return self.engine.chat(user_input)
