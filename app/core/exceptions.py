class AetherError(Exception):
    """Base exception for all Aether errors."""


class ConfigurationError(AetherError):
    """Raised when configuration is invalid."""


class LLMError(AetherError):
    """Base exception for all LLM-related errors."""


class LLMConnectionError(LLMError):
    """Raised when Aether cannot connect to the configured LLM."""


class LLMResponseError(LLMError):
    """Raised when the LLM returns an invalid response."""


class UnsupportedProviderError(LLMError):
    """Raised when the configured LLM provider is unsupported."""


class SessionError(AetherError):
    """Raised for session-related errors."""


class PromptError(AetherError):
    """Raised when prompt construction fails."""


class ToolError(AetherError):
    """Base exception for tool-related errors."""
