from __future__ import annotations

from pathlib import Path

from core.result import Result
from engine.context import WorkflowContext
from engine.step import BaseStep
from engine.workflow import Workflow
from services.project_manifest import write_project_manifest


class WriteProjectManifestStep(BaseStep):
    def __init__(self, *, output_path: str | Path) -> None:
        super().__init__(
            "write_project_manifest",
            description="Write pipeline metadata to manifest.json.",
        )
        self.output_path = Path(output_path)

    def execute(
        self,
        context: WorkflowContext,
    ) -> Result[WorkflowContext]:
        try:
            path = write_project_manifest(
                context,
                self.output_path,
            )
            context.put("project_manifest", path)
            return Result.ok(context)
        except Exception as exc:
            return Result.from_exception(exc)


def build_project_manifest_workflow(
    *,
    output_path: str | Path,
) -> Workflow:
    return Workflow(
        "project_manifest",
        steps=[
            WriteProjectManifestStep(output_path=output_path),
        ],
    )
