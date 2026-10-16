from __future__ import annotations

from pathlib import Path

from app.embedding.base import BaseEmbedder
from app.rag.chunker import BaseChunker, TextChunker
from app.rag.indexer import DocumentIndexer
from app.rag.models import Chunk, Document, SearchResult
from app.rag.retriever import DocumentRetriever
from app.rag.stores.chunk_store import BaseChunkStore, InMemoryChunkStore
from app.vectorstore.base import BaseVectorStore
from app.vectorstore.in_memory import InMemoryVectorStore


class RAGPipeline:
    """High-level facade orchestrating document indexing and semantic retrieval."""

    def __init__(
        self,
        indexer: DocumentIndexer,
        retriever: DocumentRetriever,
    ) -> None:
        self.indexer = indexer
        self.retriever = retriever

    @classmethod
    def create(
        cls,
        embedder: BaseEmbedder,
        chunk_store: BaseChunkStore | None = None,
        vector_store: BaseVectorStore | None = None,
        chunker: BaseChunker | None = None,
    ) -> RAGPipeline:
        """Convenience factory to create a fully wired RAG pipeline."""
        c_store = chunk_store if chunk_store is not None else InMemoryChunkStore()
        v_store = vector_store if vector_store is not None else InMemoryVectorStore()
        t_chunker = chunker if chunker is not None else TextChunker()

        indexer = DocumentIndexer(
            embedder=embedder,
            chunk_store=c_store,
            vector_store=v_store,
            chunker=t_chunker,
        )
        retriever = DocumentRetriever(
            embedder=embedder,
            chunk_store=c_store,
            vector_store=v_store,
        )
        return cls(indexer=indexer, retriever=retriever)

    def reindex(self) -> int:
        """Re-embed all stored chunks into the vector store."""
        return self.indexer.reindex()

    def remove_source(self, source: str) -> None:
        """Remove all chunks associated with a source path."""
        self.indexer.remove_source(source)

    def index_document(self, document: Document) -> list[Chunk]:
        """Index a single Document object."""
        return self.indexer.index_document(document)

    def index_file(self, path: str | Path) -> list[Chunk]:
        """Load and index a single document file."""
        return self.indexer.index_file(path)

    def index_directory(
        self,
        path: str | Path,
        recursive: bool = True,
    ) -> list[Chunk]:
        """Load and index all supported documents from a directory."""
        return self.indexer.index_directory(path, recursive=recursive)

    def retrieve(
        self,
        query: str,
        limit: int = 3,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """Search for relevant chunks."""
        return self.retriever.retrieve(query=query, limit=limit, min_score=min_score)

    def format_context(self, results: list[SearchResult]) -> str:
        """Format retrieved search results into a clean context block with citations."""
        if not results:
            return ""

        blocks: list[str] = ["Relevant Context:"]
        for idx, res in enumerate(results, start=1):
            source = res.chunk.source or "unknown"
            blocks.append(f"[{idx}] Source: {source}\n{res.chunk.content}")

        return "\n\n".join(blocks)
