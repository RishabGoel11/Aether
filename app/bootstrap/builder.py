from pathlib import Path

from app.bootstrap.application import Application
from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.core.session import Session
from app.llm.factory import LLMFactory
from app.logger.config import configure_logging
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore


class ApplicationBuilder:
    """
    Builds and configures an Aether application.
    """

    def build(self) -> Application:
        settings = ConfigLoader().load()

        configure_logging(settings.logging)

        llm = LLMFactory.create(settings.llm)

        session = Session()

        memory_manager = MemoryManager(
            JsonMemoryStore(Path("data") / "memories.json")
        )

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
        )