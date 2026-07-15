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


def test_chat_creates_debug_collector(engine):
    engine.chat("Hello")

    assert engine.debug_collector is not None


def test_chat_records_debug_information(engine):
    engine.chat("Hello")

    debug = engine.debug_collector.debug_info

    assert debug.response_time_ms is not None
    assert debug.response_time_ms >= 0

    # Prompt contains:
    # 1 System message
    # 1 User message
    assert debug.message_count == 2

    assert debug.prompt_length > 0


def test_chat_records_debug_events(engine):
    engine.chat("Hello")

    debug = engine.debug_collector.debug_info

    event_names = [event.name for event in debug.events]

    assert "Conversation started" in event_names
    assert "User message added" in event_names
    assert "Prompt built" in event_names
    assert "LLM request started" in event_names
    assert "LLM response received" in event_names
    assert "Assistant message stored" in event_names


def test_chat_creates_new_debug_collector_per_request(engine):
    engine.chat("Hello")
    first_collector = engine.debug_collector

    engine.chat("Hi again")
    second_collector = engine.debug_collector

    assert first_collector is not second_collector


def test_chat_finishes_debug_collection_on_exception(
    engine,
    fake_llm,
):
    fake_llm.exception = RuntimeError("LLM unavailable")

    with pytest.raises(RuntimeError):
        engine.chat("Hello")

    debug = engine.debug_collector.debug_info

    assert debug.response_time_ms is not None
