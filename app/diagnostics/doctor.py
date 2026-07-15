from app.diagnostics.checks import (
    check_configuration,
    check_model,
    check_ollama_installation,
    check_ollama_server,
    check_python_version,
)
from app.diagnostics.models import DiagnosticReport


class Doctor:
    """
    Runs all application diagnostics.
    """

    def run(self) -> DiagnosticReport:
        report = DiagnosticReport()

        report.results.extend(
            [
                check_python_version(),
                check_configuration(),
                check_ollama_installation(),
                check_ollama_server(),
                check_model(),
            ]
        )

        return report
