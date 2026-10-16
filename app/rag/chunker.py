from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from app.rag.models import Chunk, Document


class BaseChunker(ABC):
    """Abstract interface for document chunking."""

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a Document into Chunks."""


class TextChunker(BaseChunker):
    """
    Splits text into chunks using sliding window with configurable size and overlap.
    Attempts to snap splits to whitespace/newlines when possible.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap cannot be negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be smaller than chunk_size ({chunk_size})"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> list[Chunk]:
        return self.chunk_text(
            text=document.content,
            source=document.source,
            document_id=document.id,
            metadata=document.metadata,
        )

    def chunk_text(
        self,
        text: str,
        source: str = "",
        document_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        stripped = text.strip()
        if not stripped:
            return []

        doc_id = document_id or uuid4()
        base_meta = dict(metadata or {})

        # If text is shorter than or equal to chunk_size, return single chunk
        if len(stripped) <= self.chunk_size:
            return [
                Chunk(
                    document_id=doc_id,
                    content=stripped,
                    chunk_index=0,
                    source=source,
                    metadata={**base_meta, "start_char": 0, "end_char": len(stripped)},
                )
            ]

        chunks: list[Chunk] = []
        start = 0
        text_len = len(text)
        index = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            # If not at the end of text, try to find a natural break near the end
            if end < text_len:
                # Look backwards for a newline or space within the overlap margin
                margin = min(self.chunk_overlap, end - start)
                break_point = -1

                for separator in ("\n\n", "\n", " "):
                    pos = text.rfind(separator, end - margin, end)
                    if pos != -1:
                        break_point = pos + len(separator)
                        break

                if break_point > start:
                    end = break_point

            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(
                    Chunk(
                        document_id=doc_id,
                        content=chunk_content,
                        chunk_index=index,
                        source=source,
                        metadata={
                            **base_meta,
                            "start_char": start,
                            "end_char": end,
                        },
                    )
                )
                index += 1

            if end >= text_len:
                break

            # Advance by (chunk_size - overlap)
            step = max(1, (end - start) - self.chunk_overlap)
            start += step

        return chunks
