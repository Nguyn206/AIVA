from __future__ import annotations


class AIVAError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(AIVAError):
    """Raised when application configuration is missing or invalid."""


class ValidationError(AIVAError):
    """Raised when input data does not satisfy application requirements."""


class WorkflowError(AIVAError):
    """Raised when a workflow cannot be created or completed."""


class StepExecutionError(WorkflowError):
    """Raised when a workflow step fails during execution."""


class ProviderError(AIVAError):
    """Raised when an external AI or media provider fails."""
