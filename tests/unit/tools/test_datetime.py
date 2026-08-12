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

    result = tool.execute(
        tool.args_schema(),
    )

    assert result.success is True

    parsed = datetime.fromisoformat(result.output)

    assert parsed.tzinfo is not None


def test_datetime_tool_supports_timezone():
    tool = DateTimeTool()

    result = tool.execute(
        tool.args_schema(timezone="Asia/Kolkata"),
    )

    assert result.success is True
    assert result.output.endswith("+05:30")


def test_datetime_tool_rejects_unknown_timezone():
    tool = DateTimeTool()

    result = tool.execute(
        tool.args_schema(timezone="Not/A/Timezone"),
    )

    assert result.success is False
    assert "Unknown timezone" in result.error