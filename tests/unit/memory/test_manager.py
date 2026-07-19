from uuid import UUID

import pytest

from app.memory.manager import MemoryManager
from app.memory.models import MemoryCategory, MemoryRecord
from app.memory.stores.base import BaseMemoryStore


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
    manager = MemoryManager(store)

    record = MemoryRecord(content="User likes Python")

    manager.remember(record)

    assert manager.get(record.id) == record


def test_remember_empty_content():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    with pytest.raises(ValueError):
        manager.remember(MemoryRecord(content="   "))


def test_forget():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    record = MemoryRecord(content="Delete me")

    manager.remember(record)

    manager.forget(record.id)

    assert manager.get(record.id) is None


def test_list():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    manager.remember(MemoryRecord(content="One"))
    manager.remember(MemoryRecord(content="Two"))

    assert len(manager.list()) == 2


def test_find_by_category():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

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
    manager = MemoryManager(store)

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("Python")

    assert results == [memory]


def test_search_is_case_insensitive():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("python")

    assert results == [memory]


def test_search_returns_empty_when_no_match():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    memory = MemoryRecord(
        content="I prefer Python.",
        category=MemoryCategory.PREFERENCE,
    )

    manager.remember(memory)

    results = manager.search_content("Rust")

    assert results == []

def test_update_memory():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    record = MemoryRecord(content="I like Python")

    manager.remember(record)

    record.content = "I like Rust"

    manager.update(record)

    updated = manager.get(record.id)

    assert updated is not None
    assert updated.content == "I like Rust"

def test_update_missing_memory():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    record = MemoryRecord(content="Does not exist")

    with pytest.raises(ValueError):
        manager.update(record)
    
def test_update_empty_content():
    store = FakeMemoryStore()
    manager = MemoryManager(store)

    record = MemoryRecord(content="Python")

    manager.remember(record)

    record.content = "   "

    with pytest.raises(ValueError):
        manager.update(record)
    
