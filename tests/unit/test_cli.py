from pathlib import Path
from unittest.mock import Mock, patch

from app.cli.commands.index import run as run_index
from app.cli.parser import create_parser
from app.rag.models import Chunk
from app.rag.pipeline import RAGPipeline


def test_parser_index_command():
    parser = create_parser()
    args = parser.parse_args(["index", "docs/guide.md"])
    assert args.command == "index"
    assert args.path == "docs/guide.md"
    assert args.recursive is True


def test_parser_index_command_no_recursive():
    parser = create_parser()
    args = parser.parse_args(["index", "docs/", "--no-recursive"])
    assert args.command == "index"
    assert args.path == "docs/"
    assert args.recursive is False


def test_cli_index_missing_path(capsys):
    run_index("nonexistent_file_xyz.txt")
    captured = capsys.readouterr()
    assert "Error: Path does not exist" in captured.out


def test_cli_index_file(tmp_path: Path, capsys):
    doc_file = tmp_path / "test.txt"
    doc_file.write_text("Test content", encoding="utf-8")

    from uuid import uuid4

    chunk = Chunk(document_id=uuid4(), content="Test content", source=str(doc_file))

    rag_mock = Mock(spec=RAGPipeline)
    rag_mock.index_file.return_value = [chunk]

    app_mock = Mock()
    app_mock.rag = rag_mock

    with patch("app.cli.commands.index.ApplicationBuilder") as builder_cls:
        builder_cls.return_value.build.return_value = app_mock
        run_index(str(doc_file))

    captured = capsys.readouterr()
    assert "Successfully indexed" in captured.out
    assert "(1 chunks)" in captured.out


def test_parser_team_command():
    parser = create_parser()
    args = parser.parse_args(["team", "Design architecture"])
    assert args.command == "team"
    assert args.goal == "Design architecture"
    assert args.show_plan is True

    args_no_plan = parser.parse_args(["team", "Design architecture", "--no-plan"])
    assert args_no_plan.show_plan is False


def test_cli_team_command(capsys):
    from app.cli.commands.team import team as run_team
    from app.multi_agent.models import TeamResult

    team_mock = Mock()
    team_mock.solve.return_value = TeamResult(
        goal="Test goal",
        final_answer="Coordinated output",
        success=True,
    )

    app_mock = Mock()
    app_mock.team = team_mock

    with patch("app.cli.commands.team.ApplicationBuilder") as builder_cls:
        builder_cls.return_value.build.return_value = app_mock
        run_team("Test goal", show_plan=False)

    captured = capsys.readouterr()
    assert "Aether Multi-Agent Team assembling" in captured.out
    assert "Coordinated output" in captured.out
