from app.diagnostics.doctor import Doctor
from app.diagnostics.renderer import DiagnosticRenderer


def run() -> None:
    """
    Run Aether diagnostics.
    """
    doctor = Doctor()

    report = doctor.run()

    print(
        DiagnosticRenderer.render(report)
    )