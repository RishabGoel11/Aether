from pathlib import Path

from app.bootstrap.application import Application
from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.embedding.factory import EmbeddingFactory
from app.llm.factory import LLMFactory
from app.logger.config import configure_logging
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore
from app.vectorstore.in_memory import InMemoryVectorStore


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

        memory_store = JsonMemoryStore(
            Path("data") / "memories.json",
        )

        embedder = EmbeddingFactory.create()

        vector_store = InMemoryVectorStore()

        memory_manager = MemoryManager(
            store=memory_store,
            embedder=embedder,
            vector_store=vector_store,
        )

        memory_retriever = MemoryRetriever(memory_manager)

        extractor = MemoryExtractor()

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
            extractor=extractor,
        )
