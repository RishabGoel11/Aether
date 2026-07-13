from app.config.config import Settings
from app.core.engine import ConversationEngine


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
    ):
        self.settings = settings
        self.engine = engine

    def chat(self, user_input: str):
        """
        Send a message to Aether.
        """
        return self.engine.chat(user_input)