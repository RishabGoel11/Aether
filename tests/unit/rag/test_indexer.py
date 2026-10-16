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
