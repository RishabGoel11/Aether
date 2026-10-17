from unittest.mock import MagicMock

from app.integrations.langchain.llm import AetherLangChainLLM
from app.llm.base import BaseLLM
from app.llm.models import LLMResponse, Message, Role, ToolCall
from app.tools.builtin.calculator import CalculatorTool


def test_aether_langchain_llm_invoke_string():
    mock_llm = MagicMock(spec=BaseLLM)
    mock_llm.generate.return_value = LLMResponse(
        content="Paris is the capital of France.",
        tool_calls=[],
    )

    lc_model = AetherLangChainLLM(mock_llm)
    ai_msg = lc_model.invoke("What is the capital of France?")

    assert ai_msg.content == "Paris is the capital of France."
    assert ai_msg.tool_calls == []

    mock_llm.generate.assert_called_once()
    called_messages = mock_llm.generate.call_args[1]["messages"]
    assert len(called_messages) == 1
    assert called_messages[0].role == Role.USER
    assert called_messages[0].content == "What is the capital of France?"


def test_aether_langchain_llm_invoke_with_tool_calls():
    mock_llm = MagicMock(spec=BaseLLM)
    tool_req = ToolCall(
        name="calculator",
        arguments={"operation": "add", "left": 10, "right": 20},
        id="call_123",
    )
    mock_llm.generate.return_value = LLMResponse(
        content="",
        tool_calls=[tool_req],
    )

    calc = CalculatorTool()
    lc_model = AetherLangChainLLM(mock_llm).bind_tools([calc])
    ai_msg = lc_model.invoke([Message(role=Role.USER, content="Compute 10 + 20")])

    assert len(ai_msg.tool_calls) == 1
    assert ai_msg.tool_calls[0]["name"] == "calculator"
    assert ai_msg.tool_calls[0]["args"] == {"operation": "add", "left": 10, "right": 20}
    assert ai_msg.tool_calls[0]["id"] == "call_123"

    # Verify tool definitions were passed to LLM generate
    called_tools = mock_llm.generate.call_args[1]["tools"]
    assert called_tools is not None
    assert len(called_tools) == 1
    assert called_tools[0].name == "calculator"
