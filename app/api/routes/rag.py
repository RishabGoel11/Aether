"""
RAG document management endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import verify_api_key
from app.api.models import IndexRequest, IndexResponse
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api/rag", tags=["RAG"], dependencies=[Depends(verify_api_key)])


@router.post("/index", response_model=IndexResponse)
def index_documents(payload: IndexRequest) -> IndexResponse:
    """Index a file or directory into the persistent RAG knowledge base."""
    app = get_application()
    if not app.rag:
        raise HTTPException(status_code=500, detail="RAG pipeline is not configured.")

    try:
        chunks = app.rag.index(payload.path, recursive=payload.recursive)
        return IndexResponse(
            path=payload.path,
            indexed_chunks=len(chunks),
            success=True,
            message=f"Successfully indexed {len(chunks)} chunks into knowledge base.",
        )
    except Exception as exc:
        return IndexResponse(
            path=payload.path,
            indexed_chunks=0,
            success=False,
            message=str(exc),
        )


@router.get("/chunks")
def list_chunks() -> dict[str, Any]:
    """List indexed document chunks available in the knowledge base."""
    app = get_application()
    if not app.rag:
        return {"chunks": []}

    chunks = app.rag.chunk_store.list()
    return {
        "chunks": [
            {
                "id": str(c.id),
                "source": c.source,
                "text": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
            }
            for c in chunks[:50]
        ]
    }
