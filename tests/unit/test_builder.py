from app.bootstrap.application import Application
from app.bootstrap.builder import ApplicationBuilder
from app.config.config import Settings
from app.llm.factory import LLMFactory
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.session.manager import SessionManager
from tests.fakes.fake_llm import FakeLLM


def test_builder_creates_application():
    builder = ApplicationBuilder()

    app = builder.build()

    assert isinstance(app, Application)
    assert isinstance(app.memory, MemoryManager)
    assert isinstance(app.session, SessionManager)
    assert isinstance(app.extractor, MemoryExtractor)


def test_builder_returns_application(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert isinstance(app, Application)


def test_builder_creates_engine(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert app.engine is not None


def test_builder_creates_settings(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert isinstance(app.settings, Settings)


def test_builder_creates_session(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert app.engine.session is not None


def test_builder_creates_memory_manager(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert isinstance(app.memory, MemoryManager)


def test_builder_creates_memory_extractor(monkeypatch):
    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: FakeLLM(),
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert isinstance(app.extractor, MemoryExtractor)


def test_builder_uses_fake_llm(monkeypatch):
    fake_llm = FakeLLM()

    monkeypatch.setattr(
        LLMFactory,
        "create",
        lambda settings: fake_llm,
    )

    builder = ApplicationBuilder()

    app = builder.build()

    assert app.engine.llm is fake_llm