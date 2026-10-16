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
from app.rag.chunker import TextChunker
from app.rag.pipeline import RAGPipeline
from app.rag.stores.json_store import JsonChunkStore
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore
from app.tools.defaults import create_default_registry
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
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

        memory_manager.reindex()

        memory_retriever = MemoryRetriever(memory_manager)

        extractor = MemoryExtractor()

        tools = create_default_registry()
        tool_executor = ToolExecutor()
        tool_policy = ToolPolicy()

        rag_pipeline = None
        if settings.rag.enabled:
            rag_chunk_store = JsonChunkStore(
                Path("data") / "rag_chunks.json",
            )
            rag_vector_store = InMemoryVectorStore()
            rag_pipeline = RAGPipeline.create(
                embedder=embedder,
                chunk_store=rag_chunk_store,
                vector_store=rag_vector_store,
                chunker=TextChunker(
                    chunk_size=settings.rag.chunk_size,
                    chunk_overlap=settings.rag.chunk_overlap,
                ),
            )
            rag_pipeline.reindex()

        engine = ConversationEngine(
            llm=llm,
            session=session,
            memory_retriever=memory_retriever,
            memory_extractor=extractor,
            memory_manager=memory_manager,
            tools=tools,
            tool_executor=tool_executor,
            tool_policy=tool_policy,
            history_window=settings.session.history_window,
            rag_pipeline=rag_pipeline,
        )

        return Application(
            settings=settings,
            engine=engine,
            memory=memory_manager,
            session=session_manager,
            extractor=extractor,
            tools=tools,
            tool_executor=tool_executor,
            rag=rag_pipeline,
        )

