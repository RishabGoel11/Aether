import pytest

from app.llm.models import Role


def test_chat_returns_llm_response(
    engine,
    fake_llm,
):
    fake_llm.response = "Hello from Aether!"

    response = engine.chat("Hi")

    assert response.content == "Hello from Aether!"


def test_chat_updates_session(
    engine,
):
    engine.chat("Hello")

    messages = engine.session.get_messages()

    assert messages[0].role == Role.USER
    assert messages[0].content == "Hello"

    assert messages[-1].role == Role.ASSISTANT
    assert messages[-1].content == "Fake response"


def test_chat_calls_llm_once(
    engine,
    fake_llm,
):
    engine.chat("Hello")

    assert fake_llm.call_count == 1


def test_chat_sends_messages_to_llm(
    engine,
    fake_llm,
):
    engine.chat("Hello")

    assert len(fake_llm.received_messages) == 1

    sent_messages = fake_llm.received_messages[0]

    assert len(sent_messages) == 2

    assert sent_messages[0].role == Role.SYSTEM
    assert sent_messages[0].content

    assert sent_messages[1].role == Role.USER
    assert sent_messages[1].content == "Hello"

def test_chat_propagates_llm_exception(
    engine,
    fake_llm,
):
    fake_llm.exception = RuntimeError("LLM unavailable")

    with pytest.raises(RuntimeError, match="LLM unavailable"):
        engine.chat("Hello")