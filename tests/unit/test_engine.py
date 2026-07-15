from app.core.engine import ConversationEngine
from app.core.session import Session
from app.llm.base import BaseLLM
from app.llm.models import (
    LLMResponse,
    Role,
)
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore


class FakeLLM(BaseLLM):
    def generate(self, messages):
        return LLMResponse(content="Hello from Fake LLM")


def create_engine(tmp_path):
    llm = FakeLLM()
    session = Session()

    memory_manager = MemoryManager(
        JsonMemoryStore(tmp_path / "memories.json")
    )

    memory_retriever = MemoryRetriever(
        memory_manager
    )

    engine = ConversationEngine(
        llm=llm,
        session=session,
        memory_retriever=memory_retriever,
    )

    return engine, session


def test_engine_returns_llm_response(tmp_path):
    engine, _ = create_engine(tmp_path)

    response = engine.chat("Hello")

    assert response.content == "Hello from Fake LLM"


def test_engine_stores_user_message(tmp_path):
    engine, session = create_engine(tmp_path)

    engine.chat("Hello")

    messages = session.get_messages()

    assert messages[0].role == Role.USER
    assert messages[0].content == "Hello"


def test_engine_stores_assistant_response(tmp_path):
    engine, session = create_engine(tmp_path)

    engine.chat("Hello")

    messages = session.get_messages()

    assert messages[1].role == Role.ASSISTANT
    assert messages[1].content == "Hello from Fake LLM"


def test_engine_retrieves_memories(tmp_path):
    engine, _ = create_engine(tmp_path)

    engine.chat("Hello")

    assert any(
        "Retrieved" in event.name
        for event in engine.debug_collector.debug_info.events
    )   