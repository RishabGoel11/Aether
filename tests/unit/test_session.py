from app.core.session import Session
from app.llm.models import Message, Role


def test_new_session_is_empty():
    session = Session()

    assert session.get_messages() == []


def test_add_message_stores_message():
    session = Session()

    message = Message(
        role=Role.USER,
        content="Hello",
    )

    session.add_message(message)

    assert session.get_messages() == [message]


def test_messages_are_returned_in_order():
    session = Session()

    message1 = Message(
        role=Role.USER,
        content="Hello",
    )

    message2 = Message(
        role=Role.ASSISTANT,
        content="Hi!",
    )

    session.add_message(message1)
    session.add_message(message2)

    assert session.get_messages() == [message1, message2]


def test_clear_removes_all_messages():
    session = Session()

    session.add_message(
        Message(
            role=Role.USER,
            content="Hello",
        )
    )

    session.clear()

    assert session.get_messages() == []
