from app.diagnostics.models import DiagnosticReport


class DiagnosticRenderer:
    """
    Renders diagnostic reports for display.
    """

    @staticmethod
    def render(report: DiagnosticReport) -> str:
        lines = [
            "Aether Doctor",
            "==============",
            "",
        ]

        for result in report.results:
            icon = "✓" if result.success else "✗"

            lines.append(f"{icon} {result.name}: {result.message}")

        lines.append("")

        if report.healthy:
            lines.append("System is healthy.")
        else:
            lines.append(f"{report.failed} issue(s) detected.")

        return "\n".join(lines)
