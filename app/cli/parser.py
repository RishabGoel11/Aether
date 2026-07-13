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

    return parser