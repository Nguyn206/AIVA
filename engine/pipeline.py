from __future__ import annotations

from collections.abc import Iterable

from core.result import Result
from engine.context import WorkflowContext
from engine.executor import ExecutionReport, WorkflowExecutor
from engine.step import BaseStep
from engine.workflow import Workflow


class Pipeline:
    """Fluent builder used to assemble and execute a video workflow."""

    def __init__(
        self,
        name: str,
        *,
        description: str = "",
        executor: WorkflowExecutor | None = None,
    ) -> None:
        self.workflow = Workflow(name, description=description)
        self.executor = executor or WorkflowExecutor()

    def then(self, step: BaseStep) -> Pipeline:
        self.workflow.add_step(step)
        return self

    def extend(self, steps: Iterable[BaseStep]) -> Pipeline:
        for step in steps:
            self.then(step)
        return self

    def run(
        self,
        context: WorkflowContext | None = None,
    ) -> Result[ExecutionReport]:
        return self.executor.run(self.workflow, context)

    def build(self) -> Workflow:
        return self.workflow
