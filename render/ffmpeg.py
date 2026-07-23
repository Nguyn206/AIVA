from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from core.helpers import ensure_directory
from core.result import Result


class BaseCommandRunner(ABC):
    @abstractmethod
    def run(self, command: list[str]) -> Result[None]:
        """Run a command and return whether it completed successfully."""


class FFmpegRunner(BaseCommandRunner):
    """Execute FFmpeg commands on the local machine."""

    def __init__(self, executable: str = "ffmpeg") -> None:
        self.executable = executable

    def health_check(self) -> Result[bool]:
        if shutil.which(self.executable) is None:
            return Result.fail(
                "FFmpeg executable was not found in PATH.",
                error_type="FFmpegNotFoundError",
            )
        return Result.ok(True)

    def run(self, command: list[str]) -> Result[None]:
        readiness = self.health_check()
        if not readiness.success:
            return Result.fail(
                readiness.error or "FFmpeg is unavailable.",
                error_type=readiness.error_type,
            )

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            return Result.from_exception(exc)

        if completed.returncode != 0:
            error = completed.stderr.strip() or completed.stdout.strip()
            return Result.fail(
                error or "FFmpeg command failed.",
                error_type="FFmpegExecutionError",
            )

        return Result.ok()


class MockFFmpegRunner(BaseCommandRunner):
    """Offline runner for tests; writes a deterministic placeholder MP4."""

    def __init__(self) -> None:
        self.commands: list[tuple[str, ...]] = []

    def run(self, command: list[str]) -> Result[None]:
        self.commands.append(tuple(command))
        output_path = Path(command[-1])
        ensure_directory(output_path.parent)
        output_path.write_bytes(
            (
                "AIVA_MOCK_RENDER\n"
                + " ".join(command)
                + "\n"
            ).encode("utf-8")
        )
        return Result.ok()
