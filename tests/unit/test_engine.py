from unittest.mock import Mock

from app.core.engine import ConversationEngine
from app.core.session import Session
from app.embedding.base import BaseEmbedder
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Role, ToolCall
from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore
from app.tools.builtin import CalculatorTool
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.vectorstore.base import BaseVectorStore


class FakeLLM(BaseLLM):
    def generate(self, messages, tools=None):
        return LLMResponse(content="Hello from Fake LLM")


def create_engine(tmp_path):
    llm = FakeLLM()
    session = Session()

    memory_store = JsonMemoryStore(
        tmp_path / "memories.json",
    )

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)
    vector_store.search.return_value = []

    memory_manager = MemoryManager(
        store=memory_store,
        embedder=embedder,
        vector_store=vector_store,
    )

    memory_retriever = MemoryRetriever(memory_manager)

    tools = ToolRegistry()
    tools.register(CalculatorTool())

    tool_executor = ToolExecutor()

    engine = ConversationEngine(
        llm=llm,
        session=session,
        memory_retriever=memory_retriever,
        memory_extractor=MemoryExtractor(),
        memory_manager=memory_manager,
        tools=tools,
        tool_executor=tool_executor,
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


def test_engine_provides_tools_to_llm(tmp_path):
    engine, _ = create_engine(tmp_path)

    original_generate = engine.llm.generate
    captured_tools = []

    def generate(messages, tools=None):
        captured_tools.extend(tools or [])
        return original_generate(messages, tools)

    engine.llm.generate = generate

    engine.chat("Hello")

    assert len(captured_tools) == 1
    assert captured_tools[0].name == "calculator"


class ToolCallingFakeLLM(BaseLLM):
    def __init__(self):
        self.calls = 0

    def generate(self, messages, tools=None):
        self.calls += 1

        if self.calls == 1:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="calculator",
                        arguments={
                            "operation": "add",
                            "left": 10,
                            "right": 5,
                        },
                    )
                ],
            )

        return LLMResponse(
            content="The answer is 15.",
        )


def test_engine_executes_tool_call(tmp_path):
    engine, session = create_engine(tmp_path)

    llm = ToolCallingFakeLLM()
    engine.llm = llm

    response = engine.chat("What is 10 + 5?")

    assert response.content == "The answer is 15."
    assert llm.calls == 2

    assert any(
        "Tool requested: calculator" in event.name
        for event in engine.debug_collector.debug_info.events
    )

    assert any(
        "Tool completed: calculator" in event.name
        for event in engine.debug_collector.debug_info.events
    )