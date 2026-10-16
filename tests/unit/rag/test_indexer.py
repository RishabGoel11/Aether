from pathlib import Path
from unittest.mock import Mock

from app.embedding.base import BaseEmbedder
from app.rag.indexer import DocumentIndexer
from app.rag.models import Document
from app.rag.stores.chunk_store import InMemoryChunkStore
from app.vectorstore.in_memory import InMemoryVectorStore


def test_indexer_indexes_document():
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    doc = Document(source="doc.txt", content="This is content to index.")
    chunks = indexer.index_document(doc)

    assert len(chunks) == 1
    assert chunk_store.get(chunks[0].id) == chunks[0]
    assert vector_store.get(chunks[0].id) == [0.1, 0.2, 0.3]
    embedder.embed.assert_called_once_with("This is content to index.")


def test_indexer_empty_document():
    embedder = Mock(spec=BaseEmbedder)
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    chunks = indexer.index_document(Document(source="empty.txt", content="   "))
    assert chunks == []
    embedder.embed.assert_not_called()


def test_indexer_index_file(tmp_path: Path):
    file = tmp_path / "article.txt"
    file.write_text("Articles are helpful text.", encoding="utf-8")

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.5, 0.5]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    chunks = indexer.index_file(file)
    assert len(chunks) == 1
    assert chunks[0].content == "Articles are helpful text."


def test_indexer_replaces_duplicate_source():
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    doc_v1 = Document(source="note.txt", content="Version 1 content")
    indexer.index_document(doc_v1)
    assert len(chunk_store.list()) == 1

    doc_v2 = Document(source="note.txt", content="Version 2 updated content")
    indexer.index_document(doc_v2)

    # Should still be 1 chunk, replaced
    all_chunks = chunk_store.list()
    assert len(all_chunks) == 1
    assert all_chunks[0].content == "Version 2 updated content"


def test_indexer_reindex():
    from uuid import uuid4
    from app.rag.models import Chunk

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.3, 0.4]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    # Pre-populate chunk store without vector store
    chunk = Chunk(document_id=uuid4(), content="Pre-existing chunk", source="old.txt")
    chunk_store.add(chunk)
    assert vector_store.get(chunk.id) is None

    indexer = DocumentIndexer(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    reindexed_count = indexer.reindex()
    assert reindexed_count == 1
    assert vector_store.get(chunk.id) == [0.3, 0.4]

    # Second call should be a no-op
    assert indexer.reindex() == 0

