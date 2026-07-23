from __future__ import annotations

from collections.abc import Iterator

from core.exceptions import ProviderError
from providers.audio.base import BaseVoiceProvider


class VoiceProviderRegistry:
    """Registry for narration providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseVoiceProvider] = {}
        self._default_name: str | None = None

    def register(
        self,
        provider: BaseVoiceProvider,
        *,
        replace: bool = False,
        make_default: bool = False,
    ) -> BaseVoiceProvider:
        if not isinstance(provider, BaseVoiceProvider):
            raise TypeError(
                "Voice providers must inherit from BaseVoiceProvider."
            )

        if provider.name in self._providers and not replace:
            raise ValueError(
                f"Voice provider already registered: {provider.name}"
            )

        self._providers[provider.name] = provider

        if make_default or self._default_name is None:
            self._default_name = provider.name

        return provider

    def get(
        self,
        name: str | None = None,
    ) -> BaseVoiceProvider:
        selected = name or self._default_name
        if selected is None:
            raise ProviderError(
                "No default voice provider is configured."
            )

        try:
            return self._providers[selected]
        except KeyError as exc:
            raise ProviderError(
                f"Voice provider is not registered: {selected}"
            ) from exc

    def set_default(self, name: str) -> None:
        if name not in self._providers:
            raise ProviderError(
                f"Voice provider is not registered: {name}"
            )
        self._default_name = name

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def __iter__(self) -> Iterator[BaseVoiceProvider]:
        for name in self.names():
            yield self._providers[name]

    def __len__(self) -> int:
        return len(self._providers)
