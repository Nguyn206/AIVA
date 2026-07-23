from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from config.runtime import RuntimeConfig


@dataclass(frozen=True, slots=True)
class PreflightCheck:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True, slots=True)
class PreflightReport:
    checks: tuple[PreflightCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def run_real_mode_preflight(
    runtime: RuntimeConfig,
) -> PreflightReport:
    checks = (
        _check_api_key(runtime),
        _check_ffmpeg(runtime),
        _check_output_root(runtime),
        _check_models(runtime),
    )
    return PreflightReport(checks=checks)


def _check_api_key(runtime: RuntimeConfig) -> PreflightCheck:
    passed = bool(runtime.openai_api_key)
    return PreflightCheck(
        name="openai_api_key",
        passed=passed,
        message=(
            "OPENAI_API_KEY is configured."
            if passed
            else "OPENAI_API_KEY is missing."
        ),
    )


def _check_ffmpeg(runtime: RuntimeConfig) -> PreflightCheck:
    executable = runtime.ffmpeg_path
    resolved = shutil.which(executable)
    passed = resolved is not None

    return PreflightCheck(
        name="ffmpeg",
        passed=passed,
        message=(
            f"FFmpeg found at: {resolved}"
            if passed
            else f"FFmpeg was not found: {executable}"
        ),
    )


def _check_output_root(runtime: RuntimeConfig) -> PreflightCheck:
    root = Path(runtime.output_root)

    try:
        root.mkdir(parents=True, exist_ok=True)
        probe = root / ".aiva-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return PreflightCheck(
            name="output_root",
            passed=True,
            message=f"Output directory is writable: {root}",
        )
    except OSError as exc:
        return PreflightCheck(
            name="output_root",
            passed=False,
            message=f"Output directory is not writable: {exc}",
        )


def _check_models(runtime: RuntimeConfig) -> PreflightCheck:
    models = {
        "llm": runtime.llm_model,
        "image": runtime.image_model,
        "voice": runtime.voice_model,
    }
    missing = [
        name
        for name, value in models.items()
        if not value.strip()
    ]

    return PreflightCheck(
        name="models",
        passed=not missing,
        message=(
            "Model names are configured."
            if not missing
            else "Missing model names: " + ", ".join(missing)
        ),
    )
