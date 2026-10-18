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


def test_multi_session_lifecycle(tmp_path):
    store_file = tmp_path / "sessions" / "default.json"
    manager = SessionManager(JsonSessionStore(store_file))

    # Initial session list contains default session
    sessions = manager.list_sessions()
    assert len(sessions) >= 1
    assert any(s["id"] == "default" for s in sessions)

    # Create a new session
    s2 = manager.create_session(title="Research on AI", session_id="research-1")
    assert s2 == "research-1"
    assert manager.active_session_id == "research-1"

    # Add message to active session
    sess = manager.load()
    sess.add_message(Message(role=Role.USER, content="Tell me about Transformers"))
    manager.save(sess)

    # List sessions and verify message count and title
    sessions = manager.list_sessions()
    r_sess = next(s for s in sessions if s["id"] == "research-1")
    assert r_sess["message_count"] == 1
    assert r_sess["is_active"] is True

    # Switch back to default
    manager.switch_session("default")
    assert manager.active_session_id == "default"
    def_sess = manager.load()
    assert len(def_sess.get_messages()) == 0

    # Switch back to research-1
    manager.switch_session("research-1")
    res_sess = manager.load()
    assert len(res_sess.get_messages()) == 1
    assert res_sess.get_messages()[0].content == "Tell me about Transformers"

    # Delete session
    success = manager.delete_session("research-1")
    assert success is True
    assert manager.active_session_id == "default"
