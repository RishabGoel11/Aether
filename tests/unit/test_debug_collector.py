from app.debug.collector import DebugCollector


def test_start_initializes_timer():
    collector = DebugCollector()

    collector.start()

    assert collector._start_time is not None


def test_finish_records_response_time():
    collector = DebugCollector()

    collector.start()
    collector.finish()

    assert collector.debug_info.response_time_ms is not None
    assert collector.debug_info.response_time_ms >= 0


def test_add_event():
    collector = DebugCollector()

    collector.add_event("Conversation started")

    assert len(collector.debug_info.events) == 1
    assert collector.debug_info.events[0].name == "Conversation started"


def test_add_event_with_metadata():
    collector = DebugCollector()

    collector.add_event(
        "LLM Called",
        provider="ollama",
        model="qwen3:8b",
    )

    event = collector.debug_info.events[0]

    assert event.metadata["provider"] == "ollama"
    assert event.metadata["model"] == "qwen3:8b"


def test_set_provider():
    collector = DebugCollector()

    collector.set_provider("ollama")

    assert collector.debug_info.provider == "ollama"


def test_set_model():
    collector = DebugCollector()

    collector.set_model("qwen3:8b")

    assert collector.debug_info.model == "qwen3:8b"


def test_set_message_count():
    collector = DebugCollector()

    collector.set_message_count(5)

    assert collector.debug_info.message_count == 5


def test_set_prompt_length():
    collector = DebugCollector()

    collector.set_prompt_length(256)

    assert collector.debug_info.prompt_length == 256
