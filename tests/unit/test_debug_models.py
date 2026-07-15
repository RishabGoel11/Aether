from app.debug.models import DebugEvent, DebugInfo


def test_debug_event_defaults():
    event = DebugEvent(name="Test Event")

    assert event.name == "Test Event"
    assert event.metadata == {}
    assert event.timestamp is not None


def test_debug_event_metadata():
    event = DebugEvent(
        name="LLM Called",
        metadata={
            "provider": "ollama",
            "model": "qwen3:8b",
        },
    )

    assert event.metadata["provider"] == "ollama"
    assert event.metadata["model"] == "qwen3:8b"


def test_debug_info_defaults():
    debug = DebugInfo()

    assert debug.provider is None
    assert debug.model is None
    assert debug.response_time_ms is None
    assert debug.message_count == 0
    assert debug.prompt_length == 0
    assert debug.events == []
    assert debug.metadata == {}


def test_debug_info_can_store_events():
    debug = DebugInfo()

    event = DebugEvent(name="Conversation started")

    debug.events.append(event)

    assert len(debug.events) == 1
    assert debug.events[0].name == "Conversation started"


def test_debug_info_can_store_metadata():
    debug = DebugInfo()

    debug.metadata["session_id"] = "123"

    assert debug.metadata["session_id"] == "123"
