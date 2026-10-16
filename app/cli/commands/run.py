"""
CLI command: aether run

Runs the agentic ReAct loop for a one-shot natural-language goal.

Usage
-----
    aether run "Research the top 3 Python web frameworks and summarise them"
    aether run "Calculate the factorial of 12" --max-steps 10 --show-trace
"""

from __future__ import annotations

from app.agent.models import StepType
from app.bootstrap.builder import ApplicationBuilder


def run(goal: str, max_steps: int = 20, show_trace: bool = False) -> None:
    """
    Execute the agentic loop for *goal* and print the result.

    Parameters
    ----------
    goal:
        Natural-language task for the agent to complete.
    max_steps:
        Maximum number of think/act/observe steps before forcing a summary.
    show_trace:
        If True, print the full step-by-step reasoning trace.
    """
    app = ApplicationBuilder().build()

    # Override max_steps if the user specified a non-default value.
    agent = app.agent
    agent.max_steps = max_steps

    print(f"\n🤖 Aether Agent starting…\n   Goal: {goal}\n")
    print("─" * 60)

    result = agent.run(goal)

    if show_trace:
        print("\n📋 Agent Trace:")
        print("─" * 60)
        for i, step in enumerate(result.trace.steps, 1):
            icon = {
                StepType.THOUGHT: "💭",
                StepType.ACTION: "🔧",
                StepType.OBSERVATION: "👁️",
                StepType.ANSWER: "✅",
            }.get(step.type, "•")
            label = step.type.value.upper()
            print(f"\n{icon} [{i}] {label}")
            if step.tool_name:
                print(f"    Tool : {step.tool_name}")
            print(f"    {step.content}")
        print("\n" + "─" * 60)

    status = "✅ Complete" if result.success else "⚠️  Max steps reached"
    print(f"\n{status}\n")
    print(f"Aether: {result.answer}\n")
