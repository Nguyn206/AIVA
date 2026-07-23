from __future__ import annotations

from core.exceptions import ProviderError


class ProviderConfigurationError(ProviderError):
    """Raised when a provider is configured incorrectly."""


class ProviderAuthenticationError(ProviderError):
    """Raised when a provider rejects authentication."""


class ProviderRequestError(ProviderError):
    """Raised when a provider request fails."""


class ProviderNotFoundError(ProviderError):
    """Raised when a provider is not registered."""
