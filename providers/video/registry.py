from __future__ import annotations

from collections.abc import Iterator

from core.exceptions import ProviderError
from providers.video.base import BaseVideoProvider


class VideoProviderRegistry:
    """Registry for scene-level video providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseVideoProvider] = {}
        self._default_name: str | None = None

    def register(
        self,
        provider: BaseVideoProvider,
        *,
        replace: bool = False,
        make_default: bool = False,
    ) -> BaseVideoProvider:
        if not isinstance(provider, BaseVideoProvider):
            raise TypeError(
                "Video providers must inherit from BaseVideoProvider."
            )

        if provider.name in self._providers and not replace:
            raise ValueError(
                f"Video provider already registered: {provider.name}"
            )

        self._providers[provider.name] = provider

        if make_default or self._default_name is None:
            self._default_name = provider.name

        return provider

    def get(
        self,
        name: str | None = None,
    ) -> BaseVideoProvider:
        selected = name or self._default_name
        if selected is None:
            raise ProviderError(
                "No default video provider is configured."
            )

        try:
            return self._providers[selected]
        except KeyError as exc:
            raise ProviderError(
                f"Video provider is not registered: {selected}"
            ) from exc

    def set_default(self, name: str) -> None:
        if name not in self._providers:
            raise ProviderError(
                f"Video provider is not registered: {name}"
            )
        self._default_name = name

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def __iter__(self) -> Iterator[BaseVideoProvider]:
        for name in self.names():
            yield self._providers[name]

    def __len__(self) -> int:
        return len(self._providers)
