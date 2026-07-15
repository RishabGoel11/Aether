from app.debug.models import DebugEvent, DebugInfo
from app.debug.renderer import DebugRenderer


def test_render_empty_debug_info():
    debug = DebugInfo()

    output = DebugRenderer.render(debug)

    assert "Aether Debug Information" in output
    assert "Provider" in output
    assert "Unknown" in output
    assert "Messages" in output
    assert "No events recorded" in output


def test_render_with_events():
    debug = DebugInfo()

    debug.events.append(DebugEvent(name="Conversation started"))

    debug.events.append(DebugEvent(name="Prompt built"))

    output = DebugRenderer.render(debug)

    assert "Conversation started" in output
    assert "Prompt built" in output


def test_render_with_metadata():
    debug = DebugInfo()

    debug.metadata["session_id"] = "123"
    debug.metadata["provider"] = "ollama"

    output = DebugRenderer.render(debug)

    assert "Metadata:" in output
    assert "session_id: 123" in output
    assert "provider: ollama" in output


def test_render_response_time():
    debug = DebugInfo(
        response_time_ms=123.456,
    )

    output = DebugRenderer.render(debug)

    assert "123.46 ms" in output


def test_render_provider_and_model():
    debug = DebugInfo(
        provider="ollama",
        model="qwen3:8b",
    )

    output = DebugRenderer.render(debug)

    assert "ollama" in output
    assert "qwen3:8b" in output
