from __future__ import annotations

from collections.abc import Iterator

from prompts.exceptions import DuplicatePromptError, PromptNotFoundError
from prompts.template import PromptTemplate


class PromptRegistry:
    """Stores reusable prompts by name and version."""

    def __init__(self) -> None:
        self._prompts: dict[str, dict[str, PromptTemplate]] = {}

    def register(
        self,
        prompt: PromptTemplate,
        *,
        replace: bool = False,
    ) -> PromptTemplate:
        versions = self._prompts.setdefault(prompt.name, {})

        if prompt.version in versions and not replace:
            raise DuplicatePromptError(
                f"Prompt already exists: {prompt.name}@{prompt.version}"
            )

        versions[prompt.version] = prompt
        return prompt

    def get(
        self,
        name: str,
        *,
        version: str | None = None,
    ) -> PromptTemplate:
        try:
            versions = self._prompts[name]
        except KeyError as exc:
            raise PromptNotFoundError(
                f"Prompt is not registered: {name}"
            ) from exc

        selected_version = version or self.latest_version(name)

        try:
            return versions[selected_version]
        except KeyError as exc:
            raise PromptNotFoundError(
                f"Prompt version is not registered: "
                f"{name}@{selected_version}"
            ) from exc

    def latest_version(self, name: str) -> str:
        if name not in self._prompts:
            raise PromptNotFoundError(
                f"Prompt is not registered: {name}"
            )

        return sorted(
            self._prompts[name],
            key=_version_key,
        )[-1]

    def contains(
        self,
        name: str,
        *,
        version: str | None = None,
    ) -> bool:
        if name not in self._prompts:
            return False
        if version is None:
            return True
        return version in self._prompts[name]

    def unregister(
        self,
        name: str,
        *,
        version: str | None = None,
    ) -> None:
        if name not in self._prompts:
            raise PromptNotFoundError(
                f"Prompt is not registered: {name}"
            )

        if version is None:
            del self._prompts[name]
            return

        try:
            del self._prompts[name][version]
        except KeyError as exc:
            raise PromptNotFoundError(
                f"Prompt version is not registered: {name}@{version}"
            ) from exc

        if not self._prompts[name]:
            del self._prompts[name]

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._prompts))

    def versions(self, name: str) -> tuple[str, ...]:
        if name not in self._prompts:
            raise PromptNotFoundError(
                f"Prompt is not registered: {name}"
            )
        return tuple(
            sorted(self._prompts[name], key=_version_key)
        )

    def clear(self) -> None:
        self._prompts.clear()

    def __iter__(self) -> Iterator[PromptTemplate]:
        for name in self.names():
            yield self.get(name)

    def __len__(self) -> int:
        return sum(len(versions) for versions in self._prompts.values())


def _version_key(version: str) -> tuple[int | str, ...]:
    parts: list[int | str] = []
    for part in version.replace("-", ".").split("."):
        parts.append(int(part) if part.isdigit() else part)
    return tuple(parts)
