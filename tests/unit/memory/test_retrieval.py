from app.memory.manager import MemoryManager
from app.memory.models import MemoryRecord
from app.memory.retrieval import MemoryRetriever
from app.memory.stores.base import BaseMemoryStore


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


def test_retrieve_empty():
    manager = MemoryManager(FakeMemoryStore())
    retriever = MemoryRetriever(manager)

    assert retriever.retrieve("anything") == []


def test_retrieve_single_memory():
    manager = MemoryManager(FakeMemoryStore())

    memory = MemoryRecord(content="User likes Python")
    manager.remember(memory)

    retriever = MemoryRetriever(manager)

    memories = retriever.retrieve("python")

    assert len(memories) == 1
    assert memories[0] == memory


def test_retrieve_limits_results():
    manager = MemoryManager(FakeMemoryStore())

    for i in range(10):
        manager.remember(MemoryRecord(content=f"Memory {i}"))

    retriever = MemoryRetriever(manager)

    memories = retriever.retrieve("anything")

    assert len(memories) == 5


def test_retrieve_ranks_relevant_memories_first():
    manager = MemoryManager(FakeMemoryStore())

    python = MemoryRecord(content="User likes Python")
    coffee = MemoryRecord(content="User likes coffee")
    aether = MemoryRecord(content="User is building Aether")

    manager.remember(coffee)
    manager.remember(aether)
    manager.remember(python)

    retriever = MemoryRetriever(manager)

    memories = retriever.retrieve("Python")

    assert memories[0] == python


def test_retrieve_is_case_insensitive():
    manager = MemoryManager(FakeMemoryStore())

    memory = MemoryRecord(content="User likes Python")

    manager.remember(memory)

    retriever = MemoryRetriever(manager)

    memories = retriever.retrieve("PYTHON")

    assert memories[0] == memory


def test_retrieve_returns_all_when_no_match():
    manager = MemoryManager(FakeMemoryStore())

    first = MemoryRecord(content="User likes coffee")
    second = MemoryRecord(content="User is building Aether")

    manager.remember(first)
    manager.remember(second)

    retriever = MemoryRetriever(manager)

    memories = retriever.retrieve("Rust")

    assert len(memories) == 2