from app.diagnostics.models import (
    DiagnosticReport,
    DiagnosticResult,
)
from app.diagnostics.renderer import DiagnosticRenderer


def test_render_empty_report():
    report = DiagnosticReport()

    output = DiagnosticRenderer.render(report)

    assert "Aether Doctor" in output
    assert "System is healthy." in output


def test_render_successful_check():
    report = DiagnosticReport(
        results=[
            DiagnosticResult(
                name="Python",
                success=True,
                message="OK",
            )
        ]
    )

    output = DiagnosticRenderer.render(report)

    assert "✓ Python: OK" in output


def test_render_failed_check():
    report = DiagnosticReport(
        results=[
            DiagnosticResult(
                name="Ollama",
                success=False,
                message="Server not running.",
            )
        ]
    )

    output = DiagnosticRenderer.render(report)

    assert "✗ Ollama: Server not running." in output
    assert "1 issue(s) detected." in output
