import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="aether",
        description="Aether - A modular, local-first AI engineering platform.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "version",
        help="Display the current Aether version.",
    )

    subparsers.add_parser(
        "chat",
        help="Start an interactive chat session.",
    )

    subparsers.add_parser(
        "doctor",
        help="Run Aether diagnostics.",
    )

    index_parser = subparsers.add_parser(
        "index",
        help="Index documents into Aether's RAG knowledge base.",
    )
    index_parser.add_argument(
        "path",
        help="File or directory path to index.",
    )
    index_parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        default=True,
        help="Do not scan subdirectories recursively.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run the agentic loop to complete a multi-step goal.",
    )
    run_parser.add_argument(
        "goal",
        help="Natural-language goal for the agent to accomplish.",
    )
    run_parser.add_argument(
        "--max-steps",
        dest="max_steps",
        type=int,
        default=20,
        help="Maximum number of think/act/observe steps (default: 20).",
    )
    run_parser.add_argument(
        "--show-trace",
        dest="show_trace",
        action="store_true",
        default=False,
        help="Print the full step-by-step reasoning trace.",
    )

    return parser
