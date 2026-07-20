from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.embedding.base import BaseEmbedder
from app.memory.manager import MemoryManager
from app.memory.models import MemoryCategory, MemoryRecord
from app.memory.stores.base import BaseMemoryStore
from app.vectorstore.base import BaseVectorStore


class FakeMemoryStore(BaseMemoryStore):
    def __init__(self):
        self.records = {}

    def load(self):
        pass

    def save(self):
        pass

    def add(self, record):
        self.records[record.id] = record
        return record

    def update(self, record):
        if record.id not in self.records:
            raise ValueError("Memory not found")

        self.records[record.id] = record
        return record

    def delete(self, memory_id: UUID):
        if memory_id not in self.records:
            raise ValueError("Memory not found")

        del self.records[memory_id]

    def get(self, memory_id: UUID):
        return self.records.get(memory_id)

    def list(self):
        return list(self.records.values())


def test_remember():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="User likes Python")

    manager.remember(record)

    assert manager.get(record.id) == record


def test_remember_empty_content():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        manager.remember(MemoryRecord(content="   "))


def test_forget():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="Delete me")

    manager.remember(record)

    manager.forget(record.id)

    assert manager.get(record.id) is None


def test_list():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    manager.remember(MemoryRecord(content="One"))
    manager.remember(MemoryRecord(content="Two"))

    assert len(manager.list()) == 2


def test_find_by_category():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    project = MemoryRecord(
        content="I'm building Aether.",
        category=MemoryCategory.PROJECT,
    )

    preference = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(project)
    manager.remember(preference)

    results = manager.find_by_category(
        MemoryCategory.PROJECT,
    )

    assert results == [project]


def test_search_returns_matching_memories():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("Python")

    assert results == [memory]


def test_search_is_case_insensitive():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("python")

    assert results == [memory]


def test_search_returns_empty_when_no_match():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("Rust")

    assert results == []


def test_update_memory():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="I like Python")

    manager.remember(record)

    record.content = "I like Rust"

    manager.update(record)

    updated = manager.get(record.id)

    assert updated is not None
    assert updated.content == "I like Rust"


def test_update_missing_memory():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="Does not exist")

    with pytest.raises(ValueError):
        manager.update(record)


def test_update_empty_content():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="Python")

    manager.remember(record)

    record.content = "   "

    with pytest.raises(ValueError):
        manager.update(record)


def test_remember_duplicate_returns_existing():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    first = MemoryRecord(content="User likes Python")
    second = MemoryRecord(content="User likes Python")

    stored = manager.remember(first)
    duplicate = manager.remember(second)

    assert stored == duplicate
    assert len(manager.list()) == 1


def test_remember_duplicate_is_case_insensitive():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    manager.remember(MemoryRecord(content="User likes Python"))
    manager.remember(MemoryRecord(content="user likes python"))

    assert len(manager.list()) == 1


def test_remember_unique_memories():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    manager.remember(MemoryRecord(content="User likes Python"))
    manager.remember(MemoryRecord(content="User likes Rust"))

    assert len(manager.list()) == 2


def test_remember_empty_memory():
    store = FakeMemoryStore()
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    with pytest.raises(ValueError):
        manager.remember(MemoryRecord(content=""))


def test_remember_indexes_memory():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="User likes Python")

    manager.remember(record)

    embedder.embed.assert_called_once_with(record.content)

    vector_store.add.assert_called_once_with(
        record.id,
        [0.1, 0.2, 0.3],
    )


def test_update_updates_vector_store():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.4, 0.5, 0.6]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="Python")

    manager.remember(record)

    embedder.reset_mock()
    vector_store.reset_mock()

    record.content = "Rust"

    manager.update(record)

    embedder.embed.assert_called_once_with("Rust")

    vector_store.update.assert_called_once_with(
        record.id,
        [0.4, 0.5, 0.6],
    )


def test_forget_deletes_vector():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    record = MemoryRecord(content="Delete me")

    manager.remember(record)

    vector_store.reset_mock()

    manager.forget(record.id)

    vector_store.delete.assert_called_once_with(
        record.id,
    )


def test_semantic_search():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    memory = MemoryRecord(content="I love Python")

    manager.remember(memory)

    vector_store.search.return_value = [memory.id]

    result = manager.semantic_search("programming")

    assert result == [memory]

    embedder.embed.assert_called_with("programming")

    vector_store.search.assert_called_once_with(
        [0.1, 0.2, 0.3],
        limit=5,
    )


def test_semantic_search_empty():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2]

    vector_store = Mock(spec=BaseVectorStore)
    vector_store.search.return_value = []

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    assert manager.semantic_search("python") == []


def test_semantic_search_skips_missing_memory():
    store = FakeMemoryStore()

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2]

    vector_store = Mock(spec=BaseVectorStore)

    manager = MemoryManager(
        store=store,
        embedder=embedder,
        vector_store=vector_store,
    )

    missing_id = uuid4()

    vector_store.search.return_value = [missing_id]

    assert manager.semantic_search("python") == []
