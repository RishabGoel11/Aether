from pathlib import Path
from unittest.mock import Mock

from app.embedding.base import BaseEmbedder
from app.rag.models import Chunk, SearchResult
from app.rag.pipeline import RAGPipeline


def test_pipeline_create_and_e2e_flow(tmp_path: Path):
    doc_file = tmp_path / "faq.txt"
    doc_file.write_text("Aether is an autonomous AI agent framework.", encoding="utf-8")

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.2, 0.4, 0.6]

    pipeline = RAGPipeline.create(embedder=embedder)

    chunks = pipeline.index_file(doc_file)
    assert len(chunks) == 1

    results = pipeline.retrieve("What is Aether?", limit=1)
    assert len(results) == 1
    assert "Aether" in results[0].chunk.content

    formatted = pipeline.format_context(results)
    assert "Relevant Context:" in formatted
    assert "[1] Source:" in formatted
    assert "Aether is an autonomous AI agent framework." in formatted


def test_pipeline_format_context_empty():
    embedder = Mock(spec=BaseEmbedder)
    pipeline = RAGPipeline.create(embedder=embedder)
    assert pipeline.format_context([]) == ""


def test_pipeline_format_context_multiple():
    embedder = Mock(spec=BaseEmbedder)
    pipeline = RAGPipeline.create(embedder=embedder)

    from uuid import uuid4

    r1 = SearchResult(
        chunk=Chunk(document_id=uuid4(), content="Passage 1", source="a.txt"),
        score=0.9,
    )
    r2 = SearchResult(
        chunk=Chunk(document_id=uuid4(), content="Passage 2", source="b.txt"),
        score=0.8,
    )

    formatted = pipeline.format_context([r1, r2])
    assert "[1] Source: a.txt" in formatted
    assert "[2] Source: b.txt" in formatted


def test_pipeline_chunk_store_property_and_index(tmp_path: Path):
    doc_file = tmp_path / "guide.txt"
    doc_file.write_text("Testing chunk store access.", encoding="utf-8")

    embedder = Mock(spec=BaseEmbedder)
    embedder.embed.return_value = [0.1, 0.2, 0.3]

    pipeline = RAGPipeline.create(embedder=embedder)
    assert pipeline.chunk_store is not None

    chunks = pipeline.index(doc_file)
    assert len(chunks) == 1
    assert len(pipeline.chunk_store.list()) == 1
    assert len(pipeline.chunk_store.get_all()) == 1
