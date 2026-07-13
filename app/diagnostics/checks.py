import importlib.util
import sys

import ollama

from app.config.loader import ConfigLoader
from app.diagnostics.models import DiagnosticResult


def check_python_version() -> DiagnosticResult:
    """
    Verify that the current Python version satisfies
    Aether's minimum requirement.
    """
    required = (3, 12)
    current = sys.version_info[:2]

    if current >= required:
        return DiagnosticResult(
            name="Python Version",
            success=True,
            message=f"Python {current[0]}.{current[1]} detected.",
        )

    return DiagnosticResult(
        name="Python Version",
        success=False,
        message=(
            f"Python {required[0]}.{required[1]} or newer is required "
            f"(found {current[0]}.{current[1]})."
        ),
    )


def check_configuration() -> DiagnosticResult:
    """
    Verify that the application configuration can be loaded.
    """
    try:
        ConfigLoader().load()

        return DiagnosticResult(
            name="Configuration",
            success=True,
            message="Configuration loaded successfully.",
        )

    except Exception as exc:
        return DiagnosticResult(
            name="Configuration",
            success=False,
            message=str(exc),
        )


def check_ollama_installation() -> DiagnosticResult:
    """
    Verify that the Ollama Python package is installed.
    """
    if importlib.util.find_spec("ollama") is not None:
        return DiagnosticResult(
            name="Ollama Package",
            success=True,
            message="Ollama Python package is installed.",
        )

    return DiagnosticResult(
        name="Ollama Package",
        success=False,
        message="Ollama Python package is not installed.",
    )


def check_ollama_server() -> DiagnosticResult:
    """
    Verify that the Ollama server is reachable.
    """
    try:
        ollama.list()

        return DiagnosticResult(
            name="Ollama Server",
            success=True,
            message="Ollama server is running.",
        )

    except Exception:
        return DiagnosticResult(
            name="Ollama Server",
            success=False,
            message="Unable to connect to the Ollama server.",
        )


def check_model() -> DiagnosticResult:
    """
    Verify that the configured model is available.
    """
    settings = ConfigLoader().load()

    try:
        models = ollama.list()

        installed = {
            model.model
            for model in models.models
        }

        if settings.llm.model in installed:
            return DiagnosticResult(
                name="Language Model",
                success=True,
                message=f"{settings.llm.model} is available.",
            )

        return DiagnosticResult(
            name="Language Model",
            success=False,
            message=f"{settings.llm.model} is not installed.",
        )

    except Exception:
        return DiagnosticResult(
            name="Language Model",
            success=False,
            message="Unable to determine installed models.",
        )