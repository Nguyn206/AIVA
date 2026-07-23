import pytest

from services.json_parser import parse_json_object


def test_parser_reads_plain_json() -> None:
    assert parse_json_object('{"ready": true}') == {"ready": True}


def test_parser_reads_fenced_json() -> None:
    text = """```json
{"ready": true}
```"""

    assert parse_json_object(text) == {"ready": True}


def test_parser_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="object"):
        parse_json_object("[1, 2, 3]")
