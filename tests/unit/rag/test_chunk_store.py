from uuid import uuid4

from app.rag.models import Chunk
from app.rag.stores.chunk_store import InMemoryChunkStore


def test_chunk_store_add_and_get():
    store = InMemoryChunkStore()
    chunk = Chunk(
        document_id=uuid4(),
        content="Test content",
        chunk_index=0,
        source="sample.txt",
    )

    store.add(chunk)
    retrieved = store.get(chunk.id)
    assert retrieved == chunk


def test_chunk_store_add_many():
    store = InMemoryChunkStore()
    doc_id = uuid4()
    chunks = [
        Chunk(document_id=doc_id, content=f"Chunk {i}", chunk_index=i, source="sample.txt")
        for i in range(3)
    ]

    store.add_many(chunks)
    assert len(store.list()) == 3


def test_chunk_store_delete():
    store = InMemoryChunkStore()
    chunk = Chunk(
        document_id=uuid4(),
        content="Delete me",
        chunk_index=0,
        source="sample.txt",
    )
    store.add(chunk)
    store.delete(chunk.id)
    assert store.get(chunk.id) is None


def test_chunk_store_delete_by_document():
    store = InMemoryChunkStore()
    doc1 = uuid4()
    doc2 = uuid4()

    c1 = Chunk(document_id=doc1, content="C1", chunk_index=0, source="d1.txt")
    c2 = Chunk(document_id=doc1, content="C2", chunk_index=1, source="d1.txt")
    c3 = Chunk(document_id=doc2, content="C3", chunk_index=0, source="d2.txt")

    store.add_many([c1, c2, c3])
    store.delete_by_document(doc1)

    remaining = store.list()
    assert len(remaining) == 1
    assert remaining[0].id == c3.id


def test_chunk_store_clear():
    store = InMemoryChunkStore()
    chunk = Chunk(
        document_id=uuid4(),
        content="Hello",
        chunk_index=0,
        source="sample.txt",
    )
    store.add(chunk)
    store.clear()
    assert store.list() == []
