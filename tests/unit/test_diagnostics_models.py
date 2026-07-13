from app.diagnostics.models import (
    DiagnosticReport,
    DiagnosticResult,
)


def test_diagnostic_result():
    result = DiagnosticResult(
        name="Python Version",
        success=True,
        message="Python 3.13 detected.",
    )

    assert result.name == "Python Version"
    assert result.success is True
    assert result.message == "Python 3.13 detected."


def test_empty_report():
    report = DiagnosticReport()

    assert report.results == []
    assert report.passed == 0
    assert report.failed == 0
    assert report.healthy is True


def test_report_with_all_successful_checks():
    report = DiagnosticReport(
        results=[
            DiagnosticResult(
                name="Python",
                success=True,
                message="OK",
            ),
            DiagnosticResult(
                name="Configuration",
                success=True,
                message="OK",
            ),
        ]
    )

    assert report.passed == 2
    assert report.failed == 0
    assert report.healthy is True


def test_report_with_failed_checks():
    report = DiagnosticReport(
        results=[
            DiagnosticResult(
                name="Python",
                success=True,
                message="OK",
            ),
            DiagnosticResult(
                name="Ollama",
                success=False,
                message="Server not running.",
            ),
        ]
    )

    assert report.passed == 1
    assert report.failed == 1
    assert report.healthy is False


def test_report_with_all_failed_checks():
    report = DiagnosticReport(
        results=[
            DiagnosticResult(
                name="Python",
                success=False,
                message="Wrong version.",
            ),
            DiagnosticResult(
                name="Configuration",
                success=False,
                message="Missing file.",
            ),
        ]
    )

    assert report.passed == 0
    assert report.failed == 2
    assert report.healthy is False