"""
Agent execution endpoint for autonomous ReAct loops.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.auth import verify_api_key
from app.api.models import RunRequest, RunResponse
from app.api.routes.chat import get_application

router = APIRouter(prefix="/api/run", tags=["Agent"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=RunResponse)
def run_agent(payload: RunRequest) -> RunResponse:
    """Execute an autonomous agentic ReAct loop for the specified goal."""
    app = get_application()
    agent = app.agent
    agent.max_steps = payload.max_steps

    try:
        result = agent.run(payload.goal)
        trace_data = [
            {
                "type": s.type.value,
                "content": s.content,
                "tool_name": s.tool_name,
                "tool_args": s.tool_args,
            }
            for s in result.trace.steps
        ]
        return RunResponse(
            goal=payload.goal,
            answer=result.answer,
            success=result.success,
            step_count=len(result.trace.steps),
            trace=trace_data,
            error=result.error,
        )
    except Exception as exc:
        return RunResponse(
            goal=payload.goal,
            answer="",
            success=False,
            step_count=0,
            trace=[],
            error=str(exc),
        )
