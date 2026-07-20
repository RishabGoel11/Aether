from unittest.mock import Mock

from app.embedding.base import BaseEmbedder
from app.memory.manager import MemoryManager
from app.memory.models import MemoryRecord
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.base import BaseMemoryStore
from app.vectorstore.base import BaseVectorStore


class FakeMemoryStore(BaseMemoryStore):
    def __init__(self):
        self.records = {}

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self.records[record.id] = record
        return record

    def update(self, record: MemoryRecord) -> MemoryRecord:
        self.records[record.id] = record
        return record

    def delete(self, memory_id):
        self.records.pop(memory_id, None)

    def get(self, memory_id):
        return self.records.get(memory_id)

    def list(self) -> list[MemoryRecord]:
        return list(self.records.values())


def create_manager():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    return manager, embedder, vector_store


def test_retrieve_empty():
    manager, _, vector_store = create_manager()

    vector_store.search.return_value = []

    retriever = MemoryRetriever(manager)

    assert retriever.retrieve("anything") == []


def test_retrieve_returns_memories():
    manager, _, vector_store = create_manager()

    memory = MemoryRecord(content="User likes Python")
    manager.remember(memory)

    vector_store.search.return_value = [memory.id]

    retriever = MemoryRetriever(manager)

    assert retriever.retrieve("python") == [memory]


def test_retrieve_respects_limit():
    manager, _, vector_store = create_manager()

    memories = []

    for i in range(10):
        memory = MemoryRecord(content=f"Memory {i}")
        manager.remember(memory)
        memories.append(memory)

    vector_store.search.return_value = [
        memory.id for memory in memories[:5]
    ]

    retriever = MemoryRetriever(manager)

    result = retriever.retrieve("anything")

    assert len(result) == 5


def test_retrieve_skips_missing_memories():
    manager, _, vector_store = create_manager()

    vector_store.search.return_value = ["missing-id"]

    retriever = MemoryRetriever(manager)

    assert retriever.retrieve("anything") == []