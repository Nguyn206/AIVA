from pathlib import Path

from core.constants import (
    APP_NAME,
    APP_VERSION,
    OUTPUT_DIR,
    PROJECT_ROOT,
    SUPPORTED_ENVIRONMENTS,
)


def test_core_constants_are_valid() -> None:
    assert APP_NAME == "AIVA"
    assert APP_VERSION
    assert isinstance(PROJECT_ROOT, Path)
    assert OUTPUT_DIR.parent == PROJECT_ROOT
    assert "development" in SUPPORTED_ENVIRONMENTS
