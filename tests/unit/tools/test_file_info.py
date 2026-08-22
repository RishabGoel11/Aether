from app.tools.builtin.file_info import FileInfoTool


def test_file_info_tool_returns_file_metadata(tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("hello")

    tool = FileInfoTool()

    result = tool.execute(
        tool.args_schema(path=str(file_path)),
    )

    assert result.success is True
    assert result.output["type"] == "file"
    assert result.output["size_bytes"] == 5


def test_file_info_tool_returns_directory_metadata(tmp_path):
    tool = FileInfoTool()

    result = tool.execute(
        tool.args_schema(path=str(tmp_path)),
    )

    assert result.success is True
    assert result.output["type"] == "directory"


def test_file_info_tool_handles_missing_path(tmp_path):
    tool = FileInfoTool()

    result = tool.execute(
        tool.args_schema(
            path=str(tmp_path / "missing.txt"),
        ),
    )

    assert result.success is False
    assert "does not exist" in result.error
