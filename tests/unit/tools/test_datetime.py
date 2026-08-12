from datetime import datetime

from app.tools.builtin.datetime import DateTimeTool


def test_datetime_tool_has_correct_definition():
    tool = DateTimeTool()

    definition = tool.definition()

    assert definition.name == "datetime"
    assert "date" in definition.description.lower()
    assert definition.input_schema["type"] == "object"


def test_datetime_tool_returns_successful_result():
    tool = DateTimeTool()

    result = tool.execute({})

    assert result.success is True

    parsed = datetime.fromisoformat(result.output)

    assert parsed.tzinfo is not None