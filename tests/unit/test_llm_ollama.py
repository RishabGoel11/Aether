from unittest.mock import patch

from app.config.config import LLMSettings
from app.llm.models import Message, Role, ToolCall
from app.llm.ollama import OllamaLLM
from app.tools.models import ToolDefinition


def create_provider() -> OllamaLLM:
    settings = LLMSettings(
        model="qwen3:8b",
        temperature=0.7,
    )

    return OllamaLLM(settings)


def test_build_tools():
    tool = ToolDefinition(
        name="calculator",
        description="Perform basic arithmetic.",
        input_schema={
            "type": "object",
            "properties": {
                "left": {"type": "number"},
                "right": {"type": "number"},
            },
        },
    )

    result = OllamaLLM._build_tools([tool])

    assert result == [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Perform basic arithmetic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "left": {"type": "number"},
                        "right": {"type": "number"},
                    },
                },
            },
        }
    ]


@patch("app.llm.ollama.ollama.chat")
def test_generate_sends_tools(mock_chat):
    mock_chat.return_value = {
        "message": {
            "content": "I will calculate that.",
            "tool_calls": [],
        }
    }

    provider = create_provider()

    tool = ToolDefinition(
        name="calculator",
        description="Perform basic arithmetic.",
        input_schema={
            "type": "object",
            "properties": {},
        },
    )

    response = provider.generate(
        [
            Message(
                role=Role.USER,
                content="Calculate 2 + 3.",
            )
        ],
        tools=[tool],
    )

    mock_chat.assert_called_once()

    call_kwargs = mock_chat.call_args.kwargs

    assert call_kwargs["model"] == "qwen3:8b"
    assert "tools" in call_kwargs
    assert call_kwargs["tools"][0]["function"]["name"] == "calculator"
    assert response.content == "I will calculate that."


@patch("app.llm.ollama.ollama.chat")
def test_generate_parses_tool_calls(mock_chat):
    mock_chat.return_value = {
        "message": {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "calculator",
                        "arguments": {
                            "operation": "add",
                            "left": 2,
                            "right": 3,
                        },
                    }
                }
            ],
        }
    }

    provider = create_provider()

    response = provider.generate(
        [
            Message(
                role=Role.USER,
                content="Calculate 2 + 3.",
            )
        ],
    )

    assert len(response.tool_calls) == 1

    tool_call = response.tool_calls[0]

    assert isinstance(tool_call, ToolCall)
    assert tool_call.name == "calculator"
    assert tool_call.arguments == {
        "operation": "add",
        "left": 2,
        "right": 3,
    }
