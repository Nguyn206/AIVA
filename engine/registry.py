from __future__ import annotations

from collections.abc import Iterator

from engine.workflow import Workflow


class WorkflowRegistry:
    """In-memory registry for reusable AI-video workflows."""

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def register(
        self,
        workflow: Workflow,
        *,
        replace: bool = False,
    ) -> Workflow:
        if not isinstance(workflow, Workflow):
            raise TypeError("Only Workflow instances can be registered.")

        if workflow.name in self._workflows and not replace:
            raise ValueError(
                f"Workflow is already registered: {workflow.name}"
            )

        self._workflows[workflow.name] = workflow
        return workflow

    def get(self, name: str) -> Workflow:
        try:
            return self._workflows[name]
        except KeyError as exc:
            raise KeyError(
                f"Workflow is not registered: {name}"
            ) from exc

    def contains(self, name: str) -> bool:
        return name in self._workflows

    def unregister(self, name: str) -> Workflow:
        try:
            return self._workflows.pop(name)
        except KeyError as exc:
            raise KeyError(
                f"Workflow is not registered: {name}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._workflows))

    def clear(self) -> None:
        self._workflows.clear()

    def __iter__(self) -> Iterator[Workflow]:
        for name in self.names():
            yield self._workflows[name]

    def __len__(self) -> int:
        return len(self._workflows)
