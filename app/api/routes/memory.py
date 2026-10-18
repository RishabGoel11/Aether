"""
Memory exploration and retrieval endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.auth import verify_api_key
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api/memory", tags=["Memory"], dependencies=[Depends(verify_api_key)])


@router.get("")
def get_memories() -> list[dict[str, Any]]:
    """Retrieve all long-term memory records."""
    app = get_application()
    records = app.memory.get_all()
    return [
        {
            "id": r.id,
            "category": r.category.value,
            "content": r.content,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in records
    ]


@router.delete("/{memory_id}")
def delete_memory(memory_id: str) -> dict[str, Any]:
    """Delete a specific memory record by ID."""
    app = get_application()
    success = app.memory.delete(memory_id)
    return {"id": memory_id, "deleted": success}
