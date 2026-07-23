from __future__ import annotations

from collections.abc import Iterator, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from core.helpers import generate_id, utc_now_iso


@dataclass(slots=True)
class WorkflowContext:
    """Shared state passed through every step of an AI-video workflow."""

    workflow_id: str = field(default_factory=lambda: generate_id("workflow"))
    project_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def put(self, key: str, value: Any) -> None:
        self._validate_key(key)
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        self._validate_key(key)
        return self.data.get(key, default)

    def require(self, key: str) -> Any:
        self._validate_key(key)
        if key not in self.data:
            raise KeyError(f"Required workflow context key is missing: {key}")
        return self.data[key]

    def update(self, values: Mapping[str, Any]) -> None:
        for key, value in values.items():
            self.put(key, value)

    def remove(self, key: str) -> Any:
        self._validate_key(key)
        return self.data.pop(key)

    def exists(self, key: str) -> bool:
        self._validate_key(key)
        return key in self.data

    def clear(self) -> None:
        self.data.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "data": deepcopy(self.data),
            "metadata": deepcopy(self.metadata),
            "created_at": self.created_at,
        }

    def __getitem__(self, key: str) -> Any:
        return self.require(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.put(key, value)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self.data

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Workflow context keys must be non-empty strings.")
