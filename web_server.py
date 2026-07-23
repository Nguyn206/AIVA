from __future__ import annotations

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from api.app import create_app

app = create_app()
web_directory = Path(__file__).parent / "web"

if web_directory.is_dir():
    app.mount(
        "/",
        StaticFiles(
            directory=web_directory,
            html=True,
        ),
        name="web",
    )
