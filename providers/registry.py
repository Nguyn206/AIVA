from __future__ import annotations

from collections.abc import Iterator

from providers.base import BaseLLMProvider
from providers.exceptions import ProviderNotFoundError


class ProviderRegistry:
    """Stores configured LLM providers for AIVA."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}
        self._default_name: str | None = None

    def register(
        self,
        provider: BaseLLMProvider,
        *,
        replace: bool = False,
        make_default: bool = False,
    ) -> BaseLLMProvider:
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError(
                "Registered providers must inherit from BaseLLMProvider."
            )

        if provider.name in self._providers and not replace:
            raise ValueError(
                f"Provider is already registered: {provider.name}"
            )

        self._providers[provider.name] = provider

        if make_default or self._default_name is None:
            self._default_name = provider.name

        return provider

    def get(self, name: str | None = None) -> BaseLLMProvider:
        selected_name = name or self._default_name
        if selected_name is None:
            raise ProviderNotFoundError("No default provider is configured.")

        try:
            return self._providers[selected_name]
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider is not registered: {selected_name}"
            ) from exc

    def set_default(self, name: str) -> None:
        if name not in self._providers:
            raise ProviderNotFoundError(
                f"Provider is not registered: {name}"
            )
        self._default_name = name

    @property
    def default_name(self) -> str | None:
        return self._default_name

    def contains(self, name: str) -> bool:
        return name in self._providers

    def unregister(self, name: str) -> BaseLLMProvider:
        try:
            provider = self._providers.pop(name)
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider is not registered: {name}"
            ) from exc

        if self._default_name == name:
            self._default_name = next(iter(self._providers), None)

        return provider

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def clear(self) -> None:
        self._providers.clear()
        self._default_name = None

    def __iter__(self) -> Iterator[BaseLLMProvider]:
        for name in self.names():
            yield self._providers[name]

    def __len__(self) -> int:
        return len(self._providers)
