import pytest

from core.result import Result


def test_success_result_can_be_unwrapped() -> None:
    result = Result.ok("ready")

    assert result.success is True
    assert result.unwrap() == "ready"
    assert bool(result) is True


def test_success_result_can_contain_none() -> None:
    result = Result.ok()

    assert result.success is True
    assert result.unwrap() is None


def test_failed_result_raises_when_unwrapped() -> None:
    result = Result.fail("boom")

    with pytest.raises(RuntimeError, match="boom"):
        result.unwrap()


def test_failed_result_requires_message() -> None:
    with pytest.raises(ValueError):
        Result.fail("   ")


def test_map_transforms_successful_value() -> None:
    result = Result.ok(3).map(lambda value: value * 2)

    assert result.unwrap() == 6


def test_map_preserves_failure() -> None:
    result = Result.fail("not ready").map(lambda value: value)

    assert result.success is False
    assert result.error == "not ready"


def test_from_exception_records_type() -> None:
    result = Result.from_exception(ValueError("invalid"))

    assert result.success is False
    assert result.error == "invalid"
    assert result.error_type == "ValueError"
