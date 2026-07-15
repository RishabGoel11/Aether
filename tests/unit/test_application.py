from app.bootstrap.application import Application
from app.config.config import Settings
from app.memory.manager import MemoryManager
from app.memory.stores.json_store import JsonMemoryStore


def test_application_stores_components(
    engine,
    memory_manager,
):
    settings = Settings()

    app = Application(
        settings=settings,
        engine=engine,
        memory=memory_manager,
    )

    assert app.settings is settings
    assert app.engine is engine
    assert app.memory is memory_manager


def test_application_chat_delegates_to_engine(
    engine,
    tmp_path,
):
    settings = Settings()

    memory = MemoryManager(JsonMemoryStore(tmp_path / "memories.json"))

    app = Application(
        settings=settings,
        engine=engine,
        memory=memory,
    )

    response = app.chat("Hello")

    assert response.content == "Fake response"
