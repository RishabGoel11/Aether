from pathlib import Path
from uuid import uuid4

from app.rag.models import Chunk
from app.rag.stores.json_store import JsonChunkStore


def test_json_chunk_store_empty(tmp_path: Path):
    store = JsonChunkStore(tmp_path / "chunks.json")
    assert store.list() == []


def test_json_chunk_store_add_and_save(tmp_path: Path):
    filepath = tmp_path / "chunks.json"
    store = JsonChunkStore(filepath)

    chunk = Chunk(
        document_id=uuid4(),
        content="Persistent content",
        chunk_index=0,
        source="docs/sample.txt",
    )
    store.add(chunk)

    assert filepath.exists()
    assert store.get(chunk.id) == chunk


def test_json_chunk_store_reload_from_disk(tmp_path: Path):
    filepath = tmp_path / "chunks.json"
    store = JsonChunkStore(filepath)

    chunk = Chunk(
        document_id=uuid4(),
        content="Persistent reload content",
        chunk_index=0,
        source="docs/sample.txt",
    )
    store.add(chunk)

    # Re-instantiate from the same file
    store2 = JsonChunkStore(filepath)
    retrieved = store2.get(chunk.id)
    assert retrieved is not None
    assert retrieved.content == "Persistent reload content"


def test_json_chunk_store_delete(tmp_path: Path):
    filepath = tmp_path / "chunks.json"
    store = JsonChunkStore(filepath)

    chunk = Chunk(
        document_id=uuid4(),
        content="To delete",
        chunk_index=0,
        source="docs/sample.txt",
    )
    store.add(chunk)
    store.delete(chunk.id)

    store2 = JsonChunkStore(filepath)
    assert store2.get(chunk.id) is None


def test_json_chunk_store_delete_by_source(tmp_path: Path):
    filepath = tmp_path / "chunks.json"
    store = JsonChunkStore(filepath)

    c1 = Chunk(document_id=uuid4(), content="C1", chunk_index=0, source="a.txt")
    c2 = Chunk(document_id=uuid4(), content="C2", chunk_index=1, source="a.txt")
    c3 = Chunk(document_id=uuid4(), content="C3", chunk_index=0, source="b.txt")

    store.add_many([c1, c2, c3])
    store.delete_by_source("a.txt")

    store2 = JsonChunkStore(filepath)
    remaining = store2.list()
    assert len(remaining) == 1
    assert remaining[0].source == "b.txt"


def test_json_chunk_store_corrupted_json(tmp_path: Path):
    filepath = tmp_path / "chunks.json"
    filepath.write_text("{not valid json...", encoding="utf-8")

    store = JsonChunkStore(filepath)
    assert store.list() == []
