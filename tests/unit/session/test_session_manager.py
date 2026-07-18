from app.core.session import Session
from app.llm.models import Message, Role
from app.session.manager import SessionManager
from app.session.stores.json_store import JsonSessionStore


def test_load_returns_new_session_when_missing(tmp_path):
    manager = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    session = manager.load()

    assert isinstance(session, Session)
    assert session.get_messages() == []


def test_save_persists_session(tmp_path):
    manager = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    session = Session()

    session.add_message(
        Message(role=Role.USER, content="Hello"),
    )

    manager.save(session)

    loaded = manager.load()

    assert loaded.get_messages()[0].content == "Hello"


def test_clear_removes_saved_session(tmp_path):
    manager = SessionManager(
        JsonSessionStore(tmp_path / "session.json"),
    )

    session = Session()

    session.add_message(
        Message(role=Role.USER, content="Hello"),
    )

    manager.save(session)

    manager.clear()

    loaded = manager.load()

    assert loaded.get_messages() == []