from __future__ import annotations

import argparse
from pathlib import Path

from config.runtime import RuntimeConfig
from services.project_registry import list_projects
from services.project_status import get_project_status
from services.resumable_runtime_factory import (
    build_resumable_mock_pipeline,
    build_resumable_real_pipeline,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aiva-project",
        description="Inspect and resume AIVA video projects.",
    )
    parser.add_argument(
        "--output-root",
        default="output",
        help="Directory containing AIVA projects.",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commands.add_parser(
        "list",
        help="List saved AIVA projects.",
    )

    status_parser = commands.add_parser(
        "status",
        help="Show the current stage of a project.",
    )
    status_parser.add_argument("project_id")

    resume_parser = commands.add_parser(
        "resume",
        help="Resume a project from its last checkpoint.",
    )
    resume_parser.add_argument("project_id")
    resume_parser.add_argument(
        "--mode",
        choices=("mock", "real"),
        default="mock",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output_root)

    if args.command == "list":
        return _handle_list(output_root)

    if args.command == "status":
        return _handle_status(output_root, args.project_id)

    if args.command == "resume":
        return _handle_resume(
            output_root,
            args.project_id,
            args.mode,
        )

    return 2


def _handle_list(output_root: Path) -> int:
    projects = list_projects(output_root)
    if not projects:
        print("No AIVA projects found.")
        return 0

    print("PROJECT ID\tSTAGE\tFINAL VIDEO")
    for project in projects:
        final_video = "yes" if project.final_video_exists else "no"
        print(
            f"{project.project_id}\t"
            f"{project.stage}\t"
            f"{final_video}"
        )
    return 0


def _handle_status(
    output_root: Path,
    project_id: str,
) -> int:
    status = get_project_status(output_root, project_id)

    if not status.project_directory.is_dir():
        print(f"Project not found: {project_id}")
        return 1

    print(f"Project: {status.project_id}")
    print(
        "Stage: "
        + (
            status.stage.value
            if status.stage is not None
            else "unknown"
        )
    )
    print(f"Checkpoint: {_yes_no(status.checkpoint_exists)}")
    print(f"Context: {_yes_no(status.context_exists)}")
    print(f"Final video: {_yes_no(status.final_video_exists)}")
    print(f"Directory: {status.project_directory}")
    return 0


def _handle_resume(
    output_root: Path,
    project_id: str,
    mode: str,
) -> int:
    try:
        if mode == "real":
            runtime = RuntimeConfig.from_env()
            runtime = RuntimeConfig(
                openai_api_key=runtime.openai_api_key,
                llm_model=runtime.llm_model,
                image_model=runtime.image_model,
                voice_model=runtime.voice_model,
                voice_name=runtime.voice_name,
                ffmpeg_path=runtime.ffmpeg_path,
                output_root=output_root,
            )
            pipeline = build_resumable_real_pipeline(runtime)
        else:
            pipeline = build_resumable_mock_pipeline(output_root)
    except Exception as exc:
        print(f"AIVA configuration error: {exc}")
        return 2

    result = pipeline.run(
        project_id=project_id,
        resume=True,
    )

    if not result.success:
        print(f"AIVA resume failed: {result.error}")
        return 1

    output = result.unwrap()
    print(f"Project: {output.project_id}")
    print(f"Resumed: {_yes_no(output.resumed)}")
    print(f"Final video: {output.final_video_path}")
    return 0


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
