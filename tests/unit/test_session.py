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


# ---------------------------------------------------------------------------
# History windowing
# ---------------------------------------------------------------------------


def _make_message(role: Role, content: str) -> Message:
    return Message(role=role, content=content)


def test_get_messages_no_window_returns_all():
    session = Session()

    for i in range(30):
        session.add_message(_make_message(Role.USER, f"msg {i}"))

    assert len(session.get_messages()) == 30


def test_get_messages_window_larger_than_history_returns_all():
    session = Session()

    session.add_message(_make_message(Role.USER, "hi"))
    session.add_message(_make_message(Role.ASSISTANT, "hello"))

    result = session.get_messages(window=50)

    assert len(result) == 2


def test_get_messages_window_trims_to_recent_messages():
    session = Session()

    for i in range(10):
        session.add_message(_make_message(Role.USER, f"msg {i}"))

    result = session.get_messages(window=4)

    assert len(result) == 4
    assert result[-1].content == "msg 9"


def test_get_messages_window_aligns_to_user_turn():
    """
    The window must start at a USER message to avoid orphaned
    tool/assistant messages at the beginning of the context.
    """
    session = Session()

    # Build: USER, ASSISTANT, USER, ASSISTANT, USER, ASSISTANT
    for i in range(3):
        session.add_message(_make_message(Role.USER, f"user {i}"))
        session.add_message(_make_message(Role.ASSISTANT, f"asst {i}"))

    # window=3 would slice starting mid-turn at an ASSISTANT message,
    # so the implementation must snap forward to the next USER.
    result = session.get_messages(window=3)

    assert result[0].role == Role.USER


def test_get_messages_window_with_single_message():
    session = Session()
    session.add_message(_make_message(Role.USER, "only"))

    result = session.get_messages(window=4)

    assert len(result) == 1
    assert result[0].content == "only"
