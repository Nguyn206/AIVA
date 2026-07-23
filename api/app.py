from __future__ import annotations

from fastapi import FastAPI

from api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AIVA Local API",
        version="0.5.0",
        description=(
            "Local API for creating and managing fully automated "
            "AI-generated videos."
        ),
    )
    app.include_router(router, prefix="/api")
    return app


app = create_app()
