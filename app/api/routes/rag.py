"""
RAG document management endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

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


@router.post("/upload", response_model=IndexResponse)
async def upload_and_index_document(file: UploadFile = File(...)) -> IndexResponse:
    """Upload a PDF, Markdown, or text document and index it into the RAG knowledge base."""
    from pathlib import Path

    app = get_application()
    if not app.rag:
        raise HTTPException(status_code=500, detail="RAG pipeline is not configured.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    allowed_exts = {".pdf", ".md", ".txt", ".json", ".rst"}
    file_path = Path(file.filename)
    if file_path.suffix.lower() not in allowed_exts:
        ext_list = ", ".join(sorted(allowed_exts))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_path.suffix}'. Allowed: {ext_list}",
        )

    uploads_dir = Path(".aether/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path = uploads_dir / file_path.name

    try:
        content = await file.read()
        target_path.write_bytes(content)

        chunks = app.rag.index(target_path)
        return IndexResponse(
            path=str(target_path),
            indexed_chunks=len(chunks),
            success=True,
            message=f"Uploaded '{file_path.name}' and indexed {len(chunks)} chunks.",
        )
    except Exception as exc:
        return IndexResponse(
            path=str(target_path),
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
