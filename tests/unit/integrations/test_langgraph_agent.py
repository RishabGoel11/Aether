from unittest.mock import MagicMock

from app.bootstrap.builder import ApplicationBuilder
from app.integrations.langgraph.agent import GraphReActAgent
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, ToolCall
from app.tools.builtin.calculator import CalculatorTool


def test_graph_react_agent_direct_answer():
    mock_llm = MagicMock(spec=BaseLLM)
    mock_llm.generate.return_value = LLMResponse(
        content="The sky is blue due to Rayleigh scattering.",
        tool_calls=[],
    )

    agent = GraphReActAgent(llm=mock_llm, tools=[CalculatorTool()])
    result = agent.run("Why is the sky blue?")

    assert result["final_answer"] == "The sky is blue due to Rayleigh scattering."
    assert len(result["steps"]) == 1
    assert result["steps"][0]["node"] == "think"


def test_graph_react_agent_tool_loop():
    mock_llm = MagicMock(spec=BaseLLM)

    # First turn: model calls calculator
    tool_req = ToolCall(
        name="calculator",
        arguments={"operation": "add", "left": 100, "right": 250},
        id="call_calc",
    )
    resp1 = LLMResponse(content="", tool_calls=[tool_req])

    # Second turn: model gives final answer based on observation
    resp2 = LLMResponse(content="100 + 250 is 350.", tool_calls=[])

    mock_llm.generate.side_effect = [resp1, resp2]

    agent = GraphReActAgent(llm=mock_llm, tools=[CalculatorTool()])
    result = agent.run("What is 100 + 250?")

    assert result["final_answer"] == "100 + 250 is 350."
    assert len(result["steps"]) == 3
    # Step 0: think (requests tool)
    assert result["steps"][0]["node"] == "think"
    assert result["steps"][0]["tool_calls"] == ["calculator"]
    # Step 1: act (executes tool, records observation)
    assert result["steps"][1]["node"] == "act"
    assert result["steps"][1]["observations"][0]["tool"] == "calculator"
    assert result["steps"][1]["observations"][0]["result"] == "350.0"
    # Step 2: think (final answer)
    assert result["steps"][2]["node"] == "think"


def test_application_integration_helpers():
    app = ApplicationBuilder().build()

    lc_model = app.get_langchain_model()
    assert lc_model is not None
    assert len(lc_model.tools) > 0

    graph_agent = app.create_graph_agent()
    assert graph_agent is not None
    assert graph_agent.graph is not None
