from uuid import uuid4

import pytest

from app.rag.chunker import TextChunker
from app.rag.models import Document


def test_chunker_invalid_params():
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        TextChunker(chunk_size=0)

    with pytest.raises(ValueError, match="chunk_overlap cannot be negative"):
        TextChunker(chunk_size=100, chunk_overlap=-1)

    with pytest.raises(ValueError, match="must be smaller than chunk_size"):
        TextChunker(chunk_size=100, chunk_overlap=100)


def test_chunker_empty_text():
    chunker = TextChunker()
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   \n\t  ") == []


def test_chunker_short_text():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text("Short text under limit.", source="short.txt")
    assert len(chunks) == 1
    assert chunks[0].content == "Short text under limit."
    assert chunks[0].chunk_index == 0
    assert chunks[0].source == "short.txt"


def test_chunker_document_input():
    doc = Document(
        source="doc.txt",
        content="Testing document chunking with a custom document instance.",
    )
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.chunk(doc)

    assert len(chunks) == 1
    assert chunks[0].document_id == doc.id
    assert chunks[0].source == "doc.txt"


def test_chunker_splits_long_text():
    long_text = "Word " * 200  # 1000 chars
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_text(long_text, source="long.txt")

    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.content) <= 250  # Allows boundary padding


def test_chunker_preserves_custom_document_id():
    custom_id = uuid4()
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_text("A" * 120, document_id=custom_id)

    assert len(chunks) > 1
    for c in chunks:
        assert c.document_id == custom_id
