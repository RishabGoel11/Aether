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

    team_parser = subparsers.add_parser(
        "team",
        help="Run collaborative multi-agent workflow (Planner, Researcher, Coder, Reviewer).",
    )
    team_parser.add_argument(
        "goal",
        help="Goal for the agent team to collaborate on.",
    )
    team_parser.add_argument(
        "--no-plan",
        dest="show_plan",
        action="store_false",
        default=True,
        help="Do not display the initial execution plan.",
    )

    voice_parser = subparsers.add_parser(
        "voice",
        help="Interactive voice assistant listening to your microphone and speaking replies.",
    )
    voice_parser.add_argument(
        "--seconds",
        dest="seconds",
        type=float,
        default=5.0,
        help="Microphone listen duration per turn in seconds (default: 5.0).",
    )
    voice_parser.add_argument(
        "--until-silence",
        dest="until_silence",
        action="store_true",
        default=False,
        help="Automatically stop recording when speech silence is detected.",
    )
    voice_parser.add_argument(
        "--no-speak",
        dest="speak_response",
        action="store_false",
        default=True,
        help="Do not speak responses aloud (text-only output).",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Launch the Aether REST API server and modern Web UI dashboard.",
    )
    serve_parser.add_argument(
        "--host",
        dest="host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind the server to (default: 127.0.0.1).",
    )
    serve_parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8000,
        help="Port number to listen on (default: 8000).",
    )
    serve_parser.add_argument(
        "--reload",
        dest="reload",
        action="store_true",
        default=False,
        help="Enable auto-reload for development.",
    )

    return parser
