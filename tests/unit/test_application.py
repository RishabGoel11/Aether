from app.bootstrap.application import Application
from app.config.config import Settings
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.stores.json_store import JsonMemoryStore
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore


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

    app = Application(
        settings=settings,
        engine=engine,
        session=session,
        memory=memory_manager,
        extractor=extractor,
    )

    assert app.settings is settings
    assert app.engine is engine
    assert app.memory is memory_manager
    assert app.session is session
    assert app.extractor is extractor


def test_application_chat_delegates_to_engine(
    engine,
    tmp_path,
):
    settings = Settings()

    memory = MemoryManager(
        JsonMemoryStore(tmp_path / "memories.json"),
    )

    session = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    extractor = MemoryExtractor()

    app = Application(
        settings=settings,
        engine=engine,
        session=session,
        memory=memory,
        extractor=extractor,
    )

    response = app.chat("Hello")

    assert response.content == "Fake response"