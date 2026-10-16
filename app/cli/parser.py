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

    return parser

