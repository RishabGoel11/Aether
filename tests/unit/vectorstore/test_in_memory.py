from __future__ import annotations

from uuid import uuid4

import pytest

from app.vectorstore.in_memory import InMemoryVectorStore


def test_add_and_get():
    store = InMemoryVectorStore()

    memory_id = uuid4()
    embedding = [1.0, 2.0, 3.0]

    store.add(memory_id, embedding)

    assert store.get(memory_id) == embedding


def test_get_missing_returns_none():
    store = InMemoryVectorStore()

    assert store.get(uuid4()) is None


def test_update():
    store = InMemoryVectorStore()

    memory_id = uuid4()

    store.add(memory_id, [1.0, 2.0])
    store.update(memory_id, [3.0, 4.0])

    assert store.get(memory_id) == [3.0, 4.0]


def test_update_missing_raises():
    store = InMemoryVectorStore()

    with pytest.raises(ValueError, match="does not exist"):
        store.update(uuid4(), [1.0, 2.0])


def test_delete():
    store = InMemoryVectorStore()

    memory_id = uuid4()

    store.add(memory_id, [1.0, 2.0])

    store.delete(memory_id)

    assert store.get(memory_id) is None


def test_delete_missing_does_not_raise():
    store = InMemoryVectorStore()

    store.delete(uuid4())


def test_search_returns_best_match():
    store = InMemoryVectorStore()

    first = uuid4()
    second = uuid4()

    store.add(first, [1.0, 0.0])
    store.add(second, [0.0, 1.0])

    result = store.search([1.0, 0.0])

    assert result[0] == first


def test_search_respects_limit():
    store = InMemoryVectorStore()

    ids = [uuid4() for _ in range(3)]

    for memory_id in ids:
        store.add(memory_id, [1.0, 0.0])

    result = store.search([1.0, 0.0], limit=2)

    assert len(result) == 2


def test_search_empty_store():
    store = InMemoryVectorStore()

    assert store.search([1.0, 0.0]) == []


def test_zero_vector_similarity():
    store = InMemoryVectorStore()

    memory_id = uuid4()

    store.add(memory_id, [0.0, 0.0])

    result = store.search([1.0, 0.0])

    assert result == [memory_id]


def test_dimension_mismatch_raises():
    store = InMemoryVectorStore()

    memory_id = uuid4()

    store.add(memory_id, [1.0, 2.0])

    with pytest.raises(
        ValueError,
        match="Embeddings must have the same dimensions.",
    ):
        store.search([1.0])
    
def test_search_returns_results_in_similarity_order():
    store = InMemoryVectorStore()

    best = uuid4()
    middle = uuid4()
    worst = uuid4()

    store.add(best, [1.0, 0.0])
    store.add(middle, [0.5, 0.5])
    store.add(worst, [0.0, 1.0])

    result = store.search([1.0, 0.0])

    assert result == [best, middle, worst]