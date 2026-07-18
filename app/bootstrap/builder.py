from pathlib import Path

from app.bootstrap.application import Application
from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.llm.factory import LLMFactory
from app.logger.config import configure_logging
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore


class ApplicationBuilder:
    """
    Builds and configures an Aether application.
    """

    def build(self) -> Application:
        settings = ConfigLoader().load()

        configure_logging(settings.logging)

        llm = LLMFactory.create(settings.llm)

        session_store = JsonSessionStore(
            Path("data") / "session.json",
        )

        session_manager = SessionManager(session_store)

        session = session_manager.load()

        memory_manager = MemoryManager(JsonMemoryStore(Path("data") / "memories.json"))

        memory_retriever = MemoryRetriever(memory_manager)

        engine = ConversationEngine(
            llm=llm,
            session=session,
            memory_retriever=memory_retriever,
        )

        return Application(
            settings=settings,
            engine=engine,
            memory=memory_manager,
            session=session_manager,
        )
