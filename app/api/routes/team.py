"""
Multi-agent collaboration endpoint for the Aether REST API.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import verify_api_key
from app.api.models import TeamRequest, TeamResponse
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api/team", tags=["Multi-Agent"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=TeamResponse)
def run_team(payload: TeamRequest) -> TeamResponse:
    """Execute collaborative multi-agent workflow across specialists."""
    app = get_application()
    if not app.team:
        raise HTTPException(status_code=500, detail="Multi-Agent team is not initialized.")

    try:
        team_result = app.team.solve(payload.goal)
        subtasks_data = [
            {
                "id": t.id,
                "title": t.title,
                "role": t.assigned_to.value,
                "status": t.status.value,
                "result": t.result,
                "dependencies": t.dependencies,
            }
            for t in (team_result.plan.tasks if team_result.plan else [])
        ]

        return TeamResponse(
            goal=payload.goal,
            final_answer=team_result.final_answer,
            success=team_result.success,
            plan_markdown=team_result.plan.to_markdown() if team_result.plan else None,
            subtasks=subtasks_data,
            error=team_result.error,
        )
    except Exception as exc:
        return TeamResponse(
            goal=payload.goal,
            final_answer="",
            success=False,
            error=str(exc),
        )
