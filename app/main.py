from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import tts, stt


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(tts.router)
    app.include_router(stt.router)

    @app.get("/", tags=["meta"])
    def index():
        return {
            "name": settings.app_name,
            "routes": ["/tts [POST]", "/stt [POST]"],
            "stt_provider": settings.stt_provider,
            "tts_default_voice": settings.tts_default_voice,
        }

    # Static UI
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @app.get("/ui", tags=["ui"])
        def ui_index():
            return FileResponse(os.path.join(static_dir, "index.html"))

        @app.get("/status", tags=["ui"])
        def ui_status():
            return FileResponse(os.path.join(static_dir, "status.html"))

    from app.metrics import metrics

    @app.get("/metrics", tags=["meta"])
    def get_metrics():
        return {"summary": metrics.summary(), "recent": metrics.recent(50)}

    return app


app = create_app()
