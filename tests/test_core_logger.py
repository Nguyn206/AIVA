import logging
from pathlib import Path

from core.logger import configure_logging, get_logger


def test_configure_logging_creates_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "test.log"

    configure_logging("DEBUG", log_file=log_file)
    logger = get_logger("tests.logger")
    logger.debug("core logger ready")

    for handler in logging.getLogger().handlers:
        handler.flush()

    assert log_file.exists()
    assert "core logger ready" in log_file.read_text(encoding="utf-8")
