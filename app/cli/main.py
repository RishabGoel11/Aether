from app.cli.commands.chat import run as chat_command
from app.cli.commands.doctor import run as doctor_command
from app.cli.commands.version import run as version_command
from app.cli.parser import create_parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "version":
        version_command()

    elif args.command == "chat":
        chat_command()

    elif args.command == "doctor":
        doctor_command()


if __name__ == "__main__":
    main()
