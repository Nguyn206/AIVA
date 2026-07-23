from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    success: bool
    value: T | None = None
    error: str | None = None
    error_type: str | None = None

    def __post_init__(self) -> None:
        if self.success and self.error is not None:
            raise ValueError("A successful result cannot contain an error.")
        if not self.success and not (self.error and self.error.strip()):
            raise ValueError("A failed result must contain an error message.")

    @classmethod
    def ok(cls, value: T | None = None) -> Result[T]:
        return cls(success=True, value=value)

    @classmethod
    def fail(
        cls,
        error: str,
        *,
        error_type: str | None = None,
    ) -> Result[T]:
        return cls(
            success=False,
            error=error,
            error_type=error_type,
        )

    @classmethod
    def from_exception(cls, exc: Exception) -> Result[T]:
        return cls.fail(
            str(exc) or exc.__class__.__name__,
            error_type=exc.__class__.__name__,
        )

    def unwrap(self) -> T:
        if not self.success:
            raise RuntimeError(self.error or "Cannot unwrap a failed result.")
        return cast(T, self.value)

    def unwrap_or(self, default: U) -> T | U:
        if self.success:
            return cast(T, self.value)
        return default

    def map(self, function: Callable[[T], U]) -> Result[U]:
        if not self.success:
            return Result.fail(
                self.error or "Unknown error",
                error_type=self.error_type,
            )

        try:
            return Result.ok(function(cast(T, self.value)))
        except Exception as exc:
            return Result.from_exception(exc)

    def bind(self, function: Callable[[T], Result[U]]) -> Result[U]:
        if not self.success:
            return Result.fail(
                self.error or "Unknown error",
                error_type=self.error_type,
            )

        try:
            return function(cast(T, self.value))
        except Exception as exc:
            return Result.from_exception(exc)

    def __bool__(self) -> bool:
        return self.success
