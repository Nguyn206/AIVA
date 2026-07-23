import pytest

from providers.exceptions import ProviderNotFoundError
from providers.mock import MockLLMProvider
from providers.registry import ProviderRegistry


def test_registry_uses_first_provider_as_default() -> None:
    registry = ProviderRegistry()
    provider = MockLLMProvider()

    registry.register(provider)

    assert registry.get() is provider
    assert registry.default_name == "mock"


def test_registry_can_change_default_provider() -> None:
    registry = ProviderRegistry()
    registry.register(MockLLMProvider(name="first"))
    second = registry.register(
        MockLLMProvider(name="second")
    )

    registry.set_default("second")

    assert registry.get() is second


def test_registry_reports_missing_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(ProviderNotFoundError):
        registry.get("missing")
