"""
Health check and diagnostics endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.models import HealthResponse
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return platform status and component availability."""
    app = get_application()
    return HealthResponse(
        status="ok",
        version="0.11.0",
        ollama_connected=True,
        tools_registered=len(app.tools.list()),
    )


@router.get("/doctor")
def run_diagnostics() -> dict[str, Any]:
    """Execute complete Aether system diagnostics suite."""
    from app.diagnostics.doctor import Doctor

    doctor = Doctor()
    report = doctor.run()
    return {
        "status": "healthy" if report.healthy else "warning",
        "passed": report.passed,
        "failed": report.failed,
        "results": [
            {
                "name": r.name,
                "status": "ok" if r.success else "failed",
                "message": r.message,
            }
            for r in report.results
        ],
    }
