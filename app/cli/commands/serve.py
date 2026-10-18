"""
Serve command for Aether REST API and Modern Web UI.
"""

import sys

import uvicorn


def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """
    Start the Aether FastAPI application server and Web UI.
    """
    url = f"http://{host}:{port}"
    print(f"\n⚡ Starting Aether Web Platform on {url}")
    print(f"📖 Interactive OpenAPI Docs: {url}/docs")
    print("Press Ctrl+C to stop the server.\n")

    try:
        uvicorn.run(
            "app.api.server:app",
            host=host,
            port=port,
            reload=reload,
        )
    except KeyboardInterrupt:
        print("\nAether server stopped gracefully.")
        sys.exit(0)
