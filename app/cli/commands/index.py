from __future__ import annotations

from pathlib import Path

from app.bootstrap.builder import ApplicationBuilder


def run(path: str, recursive: bool = True) -> None:
    """
    Index documents into Aether's RAG knowledge base.
    """
    target = Path(path)
    if not target.exists():
        print(f"Error: Path does not exist: {target}")
        return

    app = ApplicationBuilder().build()
    if app.rag is None:
        print("Error: RAG pipeline is disabled in settings.")
        return

    if target.is_file():
        chunks = app.rag.index_file(target)
        print(f"Successfully indexed '{target}' ({len(chunks)} chunks).")
    elif target.is_dir():
        chunks = app.rag.index_directory(target, recursive=recursive)
        print(f"Successfully indexed directory '{target}' ({len(chunks)} chunks).")
    else:
        print(f"Error: Invalid path: {target}")
