from app.config.config import Settings
from app.core.engine import ConversationEngine
from app.memory.extractor import MemoryExtractor
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
        extractor: MemoryExtractor,
    ):
        self.settings = settings
        self.engine = engine
        self.session = session
        self.memory = memory
        self.extractor = extractor

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
