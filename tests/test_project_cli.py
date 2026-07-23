from project_cli import build_parser


def test_project_cli_parses_list_command() -> None:
    args = build_parser().parse_args(["list"])

    assert args.command == "list"
    assert args.output_root == "output"


def test_project_cli_parses_resume_command() -> None:
    args = build_parser().parse_args(
        [
            "--output-root",
            "videos",
            "resume",
            "video-123",
            "--mode",
            "mock",
        ]
    )

    assert args.command == "resume"
    assert args.project_id == "video-123"
    assert args.mode == "mock"
    assert args.output_root == "videos"
