from app.diagnostics.checks import (
    check_configuration,
    check_model,
    check_ollama_installation,
    check_ollama_server,
    check_python_version,
)


def test_check_python_version():
    result = check_python_version()

    assert result.name == "Python Version"
    assert isinstance(result.success, bool)
    assert result.message


def test_check_configuration():
    result = check_configuration()

    assert result.name == "Configuration"
    assert isinstance(result.success, bool)
    assert result.message

def test_check_ollama_installation():
    result = check_ollama_installation()

    assert result.name == "Ollama Package"
    assert isinstance(result.success, bool)
    assert result.message


def test_check_ollama_server():
    result = check_ollama_server()

    assert result.name == "Ollama Server"
    assert isinstance(result.success, bool)
    assert result.message


def test_check_model():
    result = check_model()

    assert result.name == "Language Model"
    assert isinstance(result.success, bool)
    assert result.message
