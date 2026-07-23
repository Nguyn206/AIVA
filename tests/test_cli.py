from cli import build_parser


def test_cli_parses_required_product_fields() -> None:
    args = build_parser().parse_args(
        [
            "--name",
            "Smart Lamp",
            "--description",
            "Adaptive desk lamp",
            "--target-market",
            "Home workers",
            "--mock",
        ]
    )

    assert args.name == "Smart Lamp"
    assert args.mock is True
