from __future__ import annotations

import math

from app.embedding.base import BaseEmbedder
from app.rag.models import SearchResult
from app.rag.stores.chunk_store import BaseChunkStore
from app.vectorstore.base import BaseVectorStore


class DocumentRetriever:
    """Retrieves relevant document chunks using vector similarity."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        chunk_store: BaseChunkStore,
        vector_store: BaseVectorStore,
    ) -> None:
        self.embedder = embedder
        self.chunk_store = chunk_store
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        limit: int = 3,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """Search for relevant chunks given a text query."""
        stripped = query.strip()
        if not stripped:
            return []

        query_embedding = self.embedder.embed(stripped)
        matched_ids = self.vector_store.search(query_embedding, limit=limit)

        results: list[SearchResult] = []
        for chunk_id in matched_ids:
            chunk = self.chunk_store.get(chunk_id)
            if chunk is None:
                continue

            stored_vec = self.vector_store.get(chunk_id)
            score = 1.0
            if stored_vec is not None:
                score = self._cosine_similarity(query_embedding, stored_vec)

            if score >= min_score:
                results.append(SearchResult(chunk=chunk, score=round(score, 4)))

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    @staticmethod
    def _cosine_similarity(
        first: list[float],
        second: list[float],
    ) -> float:
        if len(first) != len(second):
            return 0.0

        dot = sum(x * y for x, y in zip(first, second, strict=True))
        norm_a = math.sqrt(sum(x * x for x in first))
        norm_b = math.sqrt(sum(y * y for y in second))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
