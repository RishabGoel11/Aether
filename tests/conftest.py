from unittest.mock import Mock

import pytest

from app.core.engine import ConversationEngine
from app.core.session import Session
from app.embedding.base import BaseEmbedder
from app.memory.manager import MemoryManager
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.json_store import JsonMemoryStore
from app.vectorstore.base import BaseVectorStore
from tests.fakes.fake_llm import FakeLLM


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def session() -> Session:
    return Session()


@pytest.fixture
def memory_manager(tmp_path):
    memory_store = JsonMemoryStore(
        tmp_path / "memories.json",
    )

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    vector_store.search.return_value = []   

    return MemoryManager(
        store=memory_store,
        embedder=embedder,
        vector_store=vector_store,
    )


@pytest.fixture
def memory_retriever(
    memory_manager: MemoryManager,
) -> MemoryRetriever:
    return MemoryRetriever(memory_manager)


@pytest.fixture
def engine(
    fake_llm: FakeLLM,
    session: Session,
    memory_retriever: MemoryRetriever,
) -> ConversationEngine:
    return ConversationEngine(
        llm=fake_llm,
        session=session,
        memory_retriever=memory_retriever,
    )
