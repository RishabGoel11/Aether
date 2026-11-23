"""Compatibility entry point for running Aether from a source checkout."""

import sys

from app.cli.main import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("chat")
    main()
