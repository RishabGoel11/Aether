from app.core.engine import ConversationEngine
from app.core.session import Session
from app.llm.base import BaseLLM
from app.llm.models import (
    LLMResponse,
    Role,
)


class FakeLLM(BaseLLM):
    def generate(self, messages):
        return LLMResponse(content="Hello from Fake LLM")


def create_engine():
    llm = FakeLLM()
    session = Session()

    engine = ConversationEngine(
        llm=llm,
        session=session,
    )

    return engine, session


def test_engine_returns_llm_response():
    engine, _ = create_engine()

    response = engine.chat("Hello")

    assert response.content == "Hello from Fake LLM"


def test_engine_stores_user_message():
    engine, session = create_engine()

    engine.chat("Hello")

    messages = session.get_messages()

    assert messages[0].role == Role.USER
    assert messages[0].content == "Hello"


def test_engine_stores_assistant_response():
    llm = FakeLLM()
    session = Session()

    engine = ConversationEngine(
        llm=llm,
        session=session,
    )

    engine.chat("Hello")

    messages = session.get_messages()

    assert messages[1].role == Role.ASSISTANT
    assert messages[1].content == "Hello from Fake LLM"
