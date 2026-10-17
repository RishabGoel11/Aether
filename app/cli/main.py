import sys

from app.cli.commands.chat import run as chat_command
from app.cli.commands.doctor import run as doctor_command
from app.cli.commands.index import run as index_command
from app.cli.commands.run import run as run_command
from app.cli.commands.team import team as team_command
from app.cli.commands.version import run as version_command
from app.cli.commands.voice import voice as voice_command
from app.cli.parser import create_parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = create_parser()

    args = parser.parse_args()

    if args.command == "version":
        version_command()

    elif args.command == "chat":
        chat_command()

    elif args.command == "doctor":
        doctor_command()

    elif args.command == "index":
        index_command(args.path, recursive=args.recursive)

    elif args.command == "run":
        run_command(
            args.goal,
            max_steps=args.max_steps,
            show_trace=args.show_trace,
        )

    elif args.command == "team":
        team_command(
            args.goal,
            show_plan=args.show_plan,
        )

    elif args.command == "voice":
        voice_command(
            seconds=args.seconds,
            until_silence=args.until_silence,
            speak_response=args.speak_response,
        )


if __name__ == "__main__":
    main()
