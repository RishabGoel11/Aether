from uuid import uuid4

from app.rag.models import Chunk, Document, SearchResult


def test_document_creation():
    doc = Document(source="test.txt", content="Hello world")
    assert doc.source == "test.txt"
    assert doc.content == "Hello world"
    assert doc.id is not None
    assert doc.metadata == {}


def test_chunk_creation():
    doc_id = uuid4()
    chunk = Chunk(
        document_id=doc_id,
        content="Chunk content",
        chunk_index=0,
        source="test.txt",
    )
    assert chunk.document_id == doc_id
    assert chunk.content == "Chunk content"
    assert chunk.chunk_index == 0
    assert chunk.source == "test.txt"


def test_search_result_creation():
    doc_id = uuid4()
    chunk = Chunk(
        document_id=doc_id,
        content="Passage",
        chunk_index=1,
        source="docs/guide.md",
    )
    result = SearchResult(chunk=chunk, score=0.88)
    assert result.chunk == chunk
    assert result.score == 0.88
