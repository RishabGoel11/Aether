from app.core.session import Session
from app.llm.models import Message, Role
from app.session.stores.json_store import JsonSessionStore


def test_save_creates_file(tmp_path):
    store = JsonSessionStore(tmp_path / "session.json")

    session = Session()
    session.add_message(
        Message(role=Role.USER, content="Hello"),
    )

    store.save(session)

    assert store.exists()


def test_load_restores_messages(tmp_path):
    store = JsonSessionStore(tmp_path / "session.json")

    session = Session()
    session.add_message(
        Message(role=Role.USER, content="Hello"),
    )
    session.add_message(
        Message(role=Role.ASSISTANT, content="Hi"),
    )

    store.save(session)

    loaded = store.load()

    messages = loaded.get_messages()

    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi"


def test_delete_removes_file(tmp_path):
    store = JsonSessionStore(tmp_path / "session.json")

    session = Session()

    store.save(session)

    assert store.exists()

    store.delete()

    assert not store.exists()


def test_exists_false_when_missing(tmp_path):
    store = JsonSessionStore(tmp_path / "session.json")

    assert not store.exists()