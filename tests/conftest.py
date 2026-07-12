import pytest

from app.core.engine import ConversationEngine
from app.core.session import Session
from tests.fakes.fake_llm import FakeLLM


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def session() -> Session:
    return Session()


@pytest.fixture
def engine(
    fake_llm: FakeLLM,
    session: Session,
) -> ConversationEngine:
    return ConversationEngine(
        llm=fake_llm,
        session=session,
    )