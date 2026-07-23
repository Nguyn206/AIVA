from __future__ import annotations

from collections.abc import Iterable, Iterator

from engine.step import BaseStep


class Workflow:
    """Ordered definition of the steps used to generate a video."""

    def __init__(
        self,
        name: str,
        *,
        description: str = "",
        steps: Iterable[BaseStep] | None = None,
    ) -> None:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Workflow name must not be empty.")

        self.name = normalized_name
        self.description = description.strip()
        self._steps: list[BaseStep] = []

        if steps is not None:
            for step in steps:
                self.add_step(step)

    @property
    def steps(self) -> tuple[BaseStep, ...]:
        return tuple(self._steps)

    def add_step(self, step: BaseStep) -> Workflow:
        if not isinstance(step, BaseStep):
            raise TypeError("Workflow steps must inherit from BaseStep.")
        if self.has_step(step.name):
            raise ValueError(f"Workflow already contains step: {step.name}")

        self._steps.append(step)
        return self

    def insert_step(self, index: int, step: BaseStep) -> Workflow:
        if not isinstance(step, BaseStep):
            raise TypeError("Workflow steps must inherit from BaseStep.")
        if self.has_step(step.name):
            raise ValueError(f"Workflow already contains step: {step.name}")

        self._steps.insert(index, step)
        return self

    def get_step(self, name: str) -> BaseStep:
        for step in self._steps:
            if step.name == name:
                return step
        raise KeyError(f"Workflow step not found: {name}")

    def has_step(self, name: str) -> bool:
        return any(step.name == name for step in self._steps)

    def remove_step(self, name: str) -> BaseStep:
        step = self.get_step(name)
        self._steps.remove(step)
        return step

    def clear(self) -> None:
        self._steps.clear()

    def __iter__(self) -> Iterator[BaseStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        return f"Workflow(name={self.name!r}, steps={len(self._steps)})"
