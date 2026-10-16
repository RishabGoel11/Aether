from unittest.mock import Mock
from uuid import uuid4

from app.embedding.base import BaseEmbedder
from app.rag.models import Chunk
from app.rag.retriever import DocumentRetriever
from app.rag.stores.chunk_store import InMemoryChunkStore
from app.vectorstore.in_memory import InMemoryVectorStore


def test_retriever_returns_results():
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.side_effect = lambda text: [1.0, 0.0] if "query" in text else [1.0, 0.0]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    doc_id = uuid4()
    chunk1 = Chunk(document_id=doc_id, content="Python guide", chunk_index=0, source="doc.md")
    chunk_store.add(chunk1)
    vector_store.add(chunk1.id, [1.0, 0.0])

    retriever = DocumentRetriever(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    results = retriever.retrieve("query about python", limit=1)
    assert len(results) == 1
    assert results[0].chunk.content == "Python guide"
    assert results[0].score == 1.0


def test_retriever_empty_query():
    embedder = Mock(spec=BaseEmbedder)
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    retriever = DocumentRetriever(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    assert retriever.retrieve("") == []
    assert retriever.retrieve("   ") == []


def test_retriever_filters_by_min_score():
    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [1.0, 0.0]

    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    doc_id = uuid4()
    # Chunk with orthogonal vector (similarity = 0.0)
    chunk = Chunk(
        document_id=doc_id,
        content="Unrelated topic",
        chunk_index=0,
        source="unrelated.txt",
    )
    chunk_store.add(chunk)
    vector_store.add(chunk.id, [0.0, 1.0])

    retriever = DocumentRetriever(
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    results = retriever.retrieve("query", min_score=0.5)
    assert results == []
