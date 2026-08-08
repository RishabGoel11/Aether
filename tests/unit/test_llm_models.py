from app.llm.models import LLMResponse, ToolCall


def test_llm_response_defaults_to_text_response():
    response = LLMResponse(content="Hello")

    assert response.content == "Hello"
    assert response.tool_calls == []


def test_tool_call_stores_call_information():
    tool_call = ToolCall(
        id="call_1",
        name="calculator",
        arguments={
            "operation": "add",
            "left": 10,
            "right": 5,
        },
    )

    assert tool_call.id == "call_1"
    assert tool_call.name == "calculator"
    assert tool_call.arguments["operation"] == "add"


def test_llm_response_can_contain_tool_calls():
    tool_call = ToolCall(
        id="call_1",
        name="calculator",
        arguments={
            "operation": "multiply",
            "left": 4,
            "right": 5,
        },
    )

    response = LLMResponse(
        content="",
        tool_calls=[tool_call],
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "calculator"
    assert response.tool_calls[0].arguments["right"] == 5
