import uuid

import pytest

from app.memory.models import MemoryRecord
from app.memory.stores.json_store import JsonMemoryStore


def test_new_store_is_empty(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")

    assert store.list() == []


def test_add_memory(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")

    record = MemoryRecord(content="User likes Python")

    store.add(record)

    assert len(store.list()) == 1
    assert store.get(record.id) == record


def test_reload_store(tmp_path):
    path = tmp_path / "memories.json"

    store1 = JsonMemoryStore(path)

    record = MemoryRecord(content="Persistent memory")

    store1.add(record)

    store2 = JsonMemoryStore(path)

    loaded = store2.get(record.id)

    assert loaded is not None
    assert loaded.content == "Persistent memory"


def test_update_memory(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")

    record = MemoryRecord(content="Old")

    store.add(record)

    updated = record.model_copy(update={"content": "New"})

    store.update(updated)

    assert store.get(record.id).content == "New"


def test_delete_memory(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")

    record = MemoryRecord(content="Delete me")

    store.add(record)

    store.delete(record.id)

    assert store.get(record.id) is None
    assert store.list() == []


def test_update_missing_memory_raises(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")

    record = MemoryRecord(content="Missing")

    import pytest

    with pytest.raises(ValueError):
        store.update(record)


def test_delete_missing_memory_raises(tmp_path):
    store = JsonMemoryStore(tmp_path / "memories.json")


    with pytest.raises(ValueError):
        store.delete(uuid.uuid4())