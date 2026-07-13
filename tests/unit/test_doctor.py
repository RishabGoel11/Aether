from app.diagnostics.doctor import Doctor
from app.diagnostics.models import DiagnosticReport


def test_doctor_returns_report():
    doctor = Doctor()

    report = doctor.run()

    assert isinstance(report, DiagnosticReport)


def test_doctor_contains_python_check():
    doctor = Doctor()

    report = doctor.run()

    names = {
        result.name
        for result in report.results
    }

    assert "Python Version" in names
    assert "Configuration" in names
    assert "Ollama Package" in names
    assert "Ollama Server" in names
    assert "Language Model" in names