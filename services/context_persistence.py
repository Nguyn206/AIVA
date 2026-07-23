from __future__ import annotations

from pathlib import Path
from typing import Any

from core.helpers import read_json, write_json
from engine.context import WorkflowContext
from schemas.video_planning import ProductInput


def save_context(
    context: WorkflowContext,
    destination: str | Path,
) -> Path:
    payload = context.snapshot()
    payload["data"] = _serialize(payload["data"])
    return write_json(destination, payload)


def load_context(path: str | Path) -> WorkflowContext:
    payload = read_json(path)
    data = dict(payload.get("data", {}))

    product = data.get("product_input")
    if isinstance(product, dict):
        data["product_input"] = ProductInput(
            name=str(product["name"]),
            description=str(product["description"]),
            target_market=str(product["target_market"]),
            product_url=product.get("product_url"),
            features=tuple(product.get("features", [])),
        )

    return WorkflowContext(
        workflow_id=str(payload["workflow_id"]),
        project_id=payload.get("project_id"),
        data=data,
        metadata=dict(payload.get("metadata", {})),
        created_at=str(payload["created_at"]),
    )


def _serialize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "to_dict"):
        return _serialize(value.to_dict())

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _serialize(getattr(value, name))
            for name in value.__dataclass_fields__
        }

    if isinstance(value, tuple):
        return [_serialize(item) for item in value]

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }

    return value
