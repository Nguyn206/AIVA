from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from time import perf_counter

from core.logger import get_logger
from core.result import Result
from engine.context import WorkflowContext

StepFunction = Callable[
    [WorkflowContext],
    WorkflowContext | Result[WorkflowContext] | None,
]


class BaseStep(ABC):
    """Atomic operation in the AI-video generation workflow."""

    def __init__(
        self,
        name: str,
        *,
        description: str = "",
        enabled: bool = True,
    ) -> None:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Step name must not be empty.")

        self.name = normalized_name
        self.description = description.strip()
        self.enabled = enabled
        self.logger = get_logger(f"engine.step.{self.name}")

    def __call__(self, context: WorkflowContext) -> Result[WorkflowContext]:
        if not self.enabled:
            self.logger.info("Skipping disabled step: %s", self.name)
            return Result.ok(context)

        started_at = perf_counter()
        self.logger.info("Starting step: %s", self.name)

        try:
            validation = self.validate(context)
            if not validation.success:
                return Result.fail(
                    validation.error
                    or f"Validation failed for step: {self.name}",
                    error_type=validation.error_type,
                )

            self.before_execute(context)
            execution = self.execute(context)

            if not execution.success:
                self.logger.error(
                    "Step failed: %s | %s",
                    self.name,
                    execution.error,
                )
                return execution

            updated_context = execution.value or context
            self.after_execute(updated_context)

            elapsed = perf_counter() - started_at
            self.logger.info(
                "Completed step: %s in %.3fs",
                self.name,
                elapsed,
            )
            return Result.ok(updated_context)
        except Exception as exc:
            elapsed = perf_counter() - started_at
            self.logger.exception(
                "Unhandled error in step %s after %.3fs",
                self.name,
                elapsed,
            )
            return Result.from_exception(exc)

    def validate(self, context: WorkflowContext) -> Result[None]:
        return Result.ok()

    def before_execute(self, context: WorkflowContext) -> None:
        return None

    def after_execute(self, context: WorkflowContext) -> None:
        return None

    @abstractmethod
    def execute(self, context: WorkflowContext) -> Result[WorkflowContext]:
        """Execute the step and return the updated workflow context."""

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, enabled={self.enabled!r})"
        )


class FunctionStep(BaseStep):
    """Convenience step backed by a Python callable."""

    def __init__(
        self,
        name: str,
        function: StepFunction,
        *,
        description: str = "",
        enabled: bool = True,
    ) -> None:
        super().__init__(name, description=description, enabled=enabled)
        self.function = function

    def execute(self, context: WorkflowContext) -> Result[WorkflowContext]:
        result = self.function(context)

        if isinstance(result, Result):
            return result
        if result is None:
            return Result.ok(context)
        if isinstance(result, WorkflowContext):
            return Result.ok(result)

        return Result.fail(
            f"Function step {self.name!r} returned unsupported type: "
            f"{type(result).__name__}",
            error_type="InvalidStepResult",
        )
