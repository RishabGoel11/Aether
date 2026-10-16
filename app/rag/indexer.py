from __future__ import annotations

from pathlib import Path

from app.embedding.base import BaseEmbedder
from app.rag.chunker import BaseChunker, TextChunker
from app.rag.loader import DocumentLoaderFactory
from app.rag.models import Chunk, Document
from app.rag.stores.chunk_store import BaseChunkStore
from app.vectorstore.base import BaseVectorStore


class DocumentIndexer:
    """Coordinates chunking, embedding, and storing documents in chunk and vector stores."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        chunk_store: BaseChunkStore,
        vector_store: BaseVectorStore,
        chunker: BaseChunker | None = None,
    ) -> None:
        self.embedder = embedder
        self.chunk_store = chunk_store
        self.vector_store = vector_store
        self.chunker = chunker or TextChunker()

    def index_document(self, document: Document) -> list[Chunk]:
        """Chunk, embed, and store a single document."""
        chunks = self.chunker.chunk(document)
        if not chunks:
            return []

        for chunk in chunks:
            embedding = self.embedder.embed(chunk.content)
            self.chunk_store.add(chunk)
            self.vector_store.add(chunk.id, embedding)

        return chunks

    def index_documents(self, documents: list[Document]) -> list[Chunk]:
        """Index multiple documents."""
        all_chunks: list[Chunk] = []
        for doc in documents:
            all_chunks.extend(self.index_document(doc))
        return all_chunks

    def index_file(self, path: str | Path) -> list[Chunk]:
        """Load and index a single document file."""
        doc = DocumentLoaderFactory.load(path)
        return self.index_document(doc)

    def index_directory(
        self,
        path: str | Path,
        recursive: bool = True,
    ) -> list[Chunk]:
        """Load and index all supported documents from a directory."""
        docs = DocumentLoaderFactory.load_directory(path, recursive=recursive)
        return self.index_documents(docs)
