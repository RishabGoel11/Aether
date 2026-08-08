from pathlib import Path

from app.bootstrap.application import Application
from app.config.config import Settings
from app.embedding.factory import EmbeddingFactory
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.stores.json_store import JsonMemoryStore
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.vectorstore.in_memory import InMemoryVectorStore


def test_application_stores_components(
    engine,
    memory_manager,
    tmp_path,
):
    settings = Settings()

    session = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    extractor = MemoryExtractor()
    tools = ToolRegistry()
    tool_executor = ToolExecutor()

    app = Application(
        settings=settings,
        engine=engine,
        session=session,
        memory=memory_manager,
        extractor=extractor,
        tools=tools,
        tool_executor=tool_executor,
    )

    assert app.settings is settings
    assert app.engine is engine
    assert app.memory is memory_manager
    assert app.session is session
    assert app.extractor is extractor
    assert app.tools is tools
    assert app.tool_executor is tool_executor


def test_application_chat_delegates_to_engine(
    engine,
    tmp_path,
):
    settings = Settings()

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

    session = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    extractor = MemoryExtractor()
    tools = ToolRegistry()
    tool_executor = ToolExecutor()

    app = Application(
        settings=settings,
        engine=engine,
        session=session,
        memory=memory_manager,
        extractor=extractor,
        tools=tools,
        tool_executor=tool_executor,
    )

    response = app.chat("Hello")

    assert response.content == "Fake response"
