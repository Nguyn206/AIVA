from __future__ import annotations

from core.exceptions import AIVAError


class PromptError(AIVAError):
    """Base exception for prompt-system failures."""


class PromptValidationError(PromptError):
    """Raised when a prompt template is invalid."""


class PromptRenderError(PromptError):
    """Raised when a prompt cannot be rendered."""


class PromptNotFoundError(PromptError):
    """Raised when a requested prompt does not exist."""


class DuplicatePromptError(PromptError):
    """Raised when a prompt name is registered more than once."""
