from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

from core.logger import get_logger
from core.result import Result
from engine.context import WorkflowContext
from engine.workflow import Workflow


@dataclass(frozen=True, slots=True)
class StepRecord:
    name: str
    success: bool
    duration_seconds: float
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    workflow_name: str
    success: bool
    context: WorkflowContext
    duration_seconds: float
    completed_steps: tuple[str, ...] = ()
    failed_step: str | None = None
    error: str | None = None
    records: tuple[StepRecord, ...] = field(default_factory=tuple)


class WorkflowExecutor:
    """Runs workflow steps sequentially and stops on the first failure."""

    def __init__(self) -> None:
        self.logger = get_logger("engine.executor")

    def run(
        self,
        workflow: Workflow,
        context: WorkflowContext | None = None,
    ) -> Result[ExecutionReport]:
        active_context = context or WorkflowContext()
        workflow_started = perf_counter()
        completed_steps: list[str] = []
        records: list[StepRecord] = []

        self.logger.info(
            "Starting workflow: %s (%d steps)",
            workflow.name,
            len(workflow),
        )

        for step in workflow:
            step_started = perf_counter()
            result = step(active_context)
            step_duration = perf_counter() - step_started

            records.append(
                StepRecord(
                    name=step.name,
                    success=result.success,
                    duration_seconds=step_duration,
                    error=result.error,
                )
            )

            if not result.success:
                self.logger.error(
                    "Workflow failed: %s at step %s",
                    workflow.name,
                    step.name,
                )
                return Result.fail(
                    result.error
                    or f"Workflow failed at step: {step.name}",
                    error_type=(
                        result.error_type or "WorkflowExecutionError"
                    ),
                )

            active_context = result.value or active_context
            completed_steps.append(step.name)

        total_duration = perf_counter() - workflow_started
        report = ExecutionReport(
            workflow_name=workflow.name,
            success=True,
            context=active_context,
            duration_seconds=total_duration,
            completed_steps=tuple(completed_steps),
            records=tuple(records),
        )
        self.logger.info(
            "Completed workflow: %s in %.3fs",
            workflow.name,
            total_duration,
        )
        return Result.ok(report)
