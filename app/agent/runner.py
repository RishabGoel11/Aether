"""
AgentRunner — ReAct-style agentic loop for Aether.

The runner implements the classic Reason → Act → Observe cycle:

    1. THOUGHT  — LLM reasons about the goal and decides what to do next.
    2. ACTION   — LLM emits a tool call.
    3. OBSERVE  — tool result is fed back into the context.
    4. Repeat until the LLM emits a plain text ANSWER (no tool call)
       or the maximum number of steps is reached.

The runner is intentionally decoupled from ConversationEngine so it can
be used standalone (e.g., from the CLI, a web API, or tests) without
needing a live chat session.
"""

from __future__ import annotations

from app.agent.models import AgentResult, AgentStep, AgentTrace, StepType
from app.llm.base import BaseLLM
from app.llm.models import Message, Role
from app.logger.logger import get_logger
from app.tools.executor import ToolExecutor
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# System prompt injected at the start of every agent run.
# ──────────────────────────────────────────────────────────────────────────────

_AGENT_SYSTEM_PROMPT = """\
You are Aether, a local-first AI agent.

Your job is to complete the USER GOAL by reasoning step-by-step and using
the tools available to you.

Instructions:
- Think carefully before each action.
- Use tools when you need external information or to perform an action.
- After receiving a tool result (observation), reason about it before
  deciding on the next step.
- When you have enough information to answer the goal completely, respond
  with a clear, concise final answer WITHOUT calling any more tools.
- Never make up tool results — always execute the tool to get real data.
- If a tool fails, try an alternative approach or explain why it cannot
  be completed.

Format your thoughts naturally; do NOT wrap them in XML or special markers.
"""


class AgentRunner:
    """
    Drives a ReAct-style agentic loop using an LLM and tool registry.

    Parameters
    ----------
    llm:
        The language model to use for reasoning.
    tools:
        Registry of available tools.
    tool_executor:
        Validates and executes tool calls.
    tool_policy:
        Access-control policy for tool execution.
    max_steps:
        Hard upper limit on total steps (thoughts + actions + observations).
        Prevents runaway loops.  Default: 20.
    """

    def __init__(
        self,
        llm: BaseLLM,
        tools: ToolRegistry,
        tool_executor: ToolExecutor,
        tool_policy: ToolPolicy,
        max_steps: int = 20,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1.")

        self.llm = llm
        self.tools = tools
        self.tool_executor = tool_executor
        self.tool_policy = tool_policy
        self.max_steps = max_steps

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def run(self, goal: str) -> AgentResult:
        """
        Execute the agentic ReAct loop for *goal* and return the result.

        Parameters
        ----------
        goal:
            The natural-language task the agent should accomplish.

        Returns
        -------
        AgentResult
            Contains the final answer, the full trace, and success flag.
        """
        logger.info("Agent run started: %s", goal[:80])

        trace = AgentTrace(goal=goal)
        messages: list[Message] = self._build_initial_messages(goal)
        tool_definitions = [
            tool.definition() for tool in self.tools.list()
        ]

        steps_taken = 0

        while steps_taken < self.max_steps:
            steps_taken += 1
            logger.debug("Agent step %d / %d", steps_taken, self.max_steps)

            response = self.llm.generate(messages, tools=tool_definitions)

            # ── Case 1: LLM wants to call a tool ─────────────────────────────
            if response.tool_calls:
                # Record the LLM's current reasoning as a THOUGHT if it also
                # produced text alongside the tool call.
                if response.content.strip():
                    thought = AgentStep(
                        type=StepType.THOUGHT,
                        content=response.content.strip(),
                    )
                    trace.add(thought)
                    messages.append(
                        Message(role=Role.ASSISTANT, content=response.content)
                    )

                # Process every tool call in the response.
                for tool_call in response.tool_calls:
                    action = AgentStep(
                        type=StepType.ACTION,
                        content=(
                            f"Calling tool '{tool_call.name}' "
                            f"with args {tool_call.arguments}"
                        ),
                        tool_name=tool_call.name,
                        tool_args=tool_call.arguments,
                    )
                    trace.add(action)

                    observation_content = self._execute_tool(
                        tool_call.name,
                        tool_call.arguments,
                    )

                    observation = AgentStep(
                        type=StepType.OBSERVATION,
                        content=observation_content,
                        tool_name=tool_call.name,
                    )
                    trace.add(observation)

                    # Feed the observation back into the message history so
                    # the LLM can reason about it on the next iteration.
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=(
                                f"Tool result for '{tool_call.name}': "
                                f"{observation_content}"
                            ),
                        )
                    )

            # ── Case 2: LLM produced a plain text answer ──────────────────────
            else:
                answer_text = response.content.strip()

                if not answer_text:
                    answer_text = (
                        "I wasn't able to produce a final answer. "
                        "Please try rephrasing your goal."
                    )

                answer_step = AgentStep(
                    type=StepType.ANSWER,
                    content=answer_text,
                )
                trace.add(answer_step)

                logger.info(
                    "Agent run complete in %d steps.", steps_taken
                )

                return AgentResult(
                    success=True,
                    answer=answer_text,
                    trace=trace,
                )

        # ── Max steps exhausted ───────────────────────────────────────────────
        logger.warning(
            "Agent run hit max_steps=%d without producing an answer.",
            self.max_steps,
        )

        # Ask the LLM to synthesise a best-effort answer from what it has.
        messages.append(
            Message(
                role=Role.USER,
                content=(
                    "You have used the maximum number of steps. "
                    "Please summarise what you have found so far and provide "
                    "the best answer you can based on the information gathered."
                ),
            )
        )

        fallback = self.llm.generate(messages, tools=[])
        fallback_text = fallback.content.strip() or (
            "The agent could not complete the task within the step limit."
        )

        fallback_step = AgentStep(
            type=StepType.ANSWER,
            content=fallback_text,
        )
        trace.add(fallback_step)

        return AgentResult(
            success=False,
            answer=fallback_text,
            trace=trace,
            error=(
                f"Agent reached the maximum step limit ({self.max_steps}) "
                "without producing a final answer."
            ),
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _build_initial_messages(self, goal: str) -> list[Message]:
        """Construct the initial message list for the run."""
        return [
            Message(role=Role.SYSTEM, content=_AGENT_SYSTEM_PROMPT),
            Message(role=Role.USER, content=f"USER GOAL: {goal}"),
        ]

    def _execute_tool(
        self,
        tool_name: str,
        arguments: dict,
    ) -> str:
        """Execute a single tool call and return the string observation."""
        try:
            tool = self.tools.get(tool_name)
        except Exception:
            return f"Tool '{tool_name}' not found in registry."

        if not self.tool_policy.is_allowed(tool.definition()):
            return f"Tool execution denied by policy: {tool_name}"

        result = self.tool_executor.execute(tool, arguments)

        if result.success:
            return str(result.output)
        else:
            return f"Tool execution failed: {result.error}"
