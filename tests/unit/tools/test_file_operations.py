from pathlib import Path

from app.tools.builtin.file_operations import (
    ListDirectoryArgs,
    ListDirectoryTool,
    ReadFileArgs,
    ReadFileTool,
    WriteFileArgs,
    WriteFileTool,
)


def test_write_file_creates_file_and_parents(tmp_path: Path):
    target = tmp_path / "nested" / "sub" / "output.txt"
    tool = WriteFileTool()

    result = tool.execute(WriteFileArgs(path=str(target), content="Hello Aether!"))

    assert result.success is True
    assert "wrote 13 characters" in result.output
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "Hello Aether!"


def test_write_file_append(tmp_path: Path):
    target = tmp_path / "log.txt"
    target.write_text("Line 1\n", encoding="utf-8")
    tool = WriteFileTool()

    result = tool.execute(WriteFileArgs(path=str(target), content="Line 2\n", append=True))

    assert result.success is True
    assert "appended to 7 characters" in result.output
    assert target.read_text(encoding="utf-8") == "Line 1\nLine 2\n"


def test_read_file_full_content(tmp_path: Path):
    target = tmp_path / "hello.txt"
    target.write_text("Hello World", encoding="utf-8")
    tool = ReadFileTool()

    result = tool.execute(ReadFileArgs(path=str(target)))

    assert result.success is True
    assert result.output == "Hello World"


def test_read_file_slices_lines(tmp_path: Path):
    target = tmp_path / "lines.txt"
    target.write_text("line0\nline1\nline2\nline3\nline4\n", encoding="utf-8")
    tool = ReadFileTool()

    result = tool.execute(ReadFileArgs(path=str(target), offset=1, max_lines=2))

    assert result.success is True
    assert result.output == "line1\nline2\n"


def test_read_file_missing_returns_error(tmp_path: Path):
    missing = tmp_path / "does_not_exist.txt"
    tool = ReadFileTool()

    result = tool.execute(ReadFileArgs(path=str(missing)))

    assert result.success is False
    assert "File not found" in result.error


def test_read_file_directory_returns_error(tmp_path: Path):
    tool = ReadFileTool()

    result = tool.execute(ReadFileArgs(path=str(tmp_path)))

    assert result.success is False
    assert "Path is not a file" in result.error


def test_read_file_size_limit_exceeded(tmp_path: Path, monkeypatch):
    target = tmp_path / "huge.txt"
    target.write_text("small content", encoding="utf-8")
    tool = ReadFileTool()

    # Artificially set MAX_READ_SIZE_BYTES low for test
    from app.tools.builtin import file_operations

    monkeypatch.setattr(file_operations, "MAX_READ_SIZE_BYTES", 5)

    result = tool.execute(ReadFileArgs(path=str(target)))

    assert result.success is False
    assert "exceeds limit" in result.error


def test_list_directory_returns_entries(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("abc", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    tool = ListDirectoryTool()

    result = tool.execute(ListDirectoryArgs(path=str(tmp_path)))

    assert result.success is True
    assert isinstance(result.output, list)
    names = {entry["name"] for entry in result.output}
    assert "file1.txt" in names
    assert "subdir" in names

    file_entry = next(e for e in result.output if e["name"] == "file1.txt")
    assert file_entry["type"] == "file"
    assert file_entry["size_bytes"] == 3

    dir_entry = next(e for e in result.output if e["name"] == "subdir")
    assert dir_entry["type"] == "directory"


def test_list_directory_missing_returns_error(tmp_path: Path):
    missing = tmp_path / "missing_dir"
    tool = ListDirectoryTool()

    result = tool.execute(ListDirectoryArgs(path=str(missing)))

    assert result.success is False
    assert "Directory not found" in result.error


def test_list_directory_file_path_returns_error(tmp_path: Path):
    target = tmp_path / "file.txt"
    target.write_text("abc", encoding="utf-8")
    tool = ListDirectoryTool()

    result = tool.execute(ListDirectoryArgs(path=str(target)))

    assert result.success is False
    assert "Path is not a directory" in result.error


def test_list_directory_max_entries(tmp_path: Path):
    for i in range(10):
        (tmp_path / f"file_{i}.txt").write_text("x", encoding="utf-8")

    tool = ListDirectoryTool()
    result = tool.execute(ListDirectoryArgs(path=str(tmp_path), max_entries=4))

    assert result.success is True
    assert len(result.output) == 4
