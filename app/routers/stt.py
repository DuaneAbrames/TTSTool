from __future__ import annotations

import os
import shutil
import tempfile
from typing import Optional

import time
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.services.stt_base import STTError, get_stt_engine
from app.metrics import metrics


router = APIRouter(prefix="/stt", tags=["stt"])


class STTResponse(BaseModel):
    provider: str
    text: str


@router.post("", response_model=STTResponse, summary="Transcribe uploaded audio to text")
async def speech_to_text(
    file: UploadFile = File(..., description="Audio file (.wav, .mp3, etc.)"),
    provider: Optional[str] = Query(None, description="Override STT provider: azure|whisper"),
):
    settings = get_settings()

    # Persist to a temp file because most engines need a file path
    suffix = os.path.splitext(file.filename or "audio")[1] or ".wav"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            await file.seek(0)
            shutil.copyfileobj(file.file, tmp)
    finally:
        await file.close()

    try:
        engine = get_stt_engine(settings, provider_override=provider)
        start = time.perf_counter()
        text = await engine.transcribe(tmp_path)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        metrics.record(
            op="stt",
            ms=elapsed_ms,
            ok=True,
            filename=file.filename or "",
        )
        return STTResponse(provider=(provider or settings.stt_provider or "unknown"), text=text)
    except STTError as exc:
        metrics.record(op="stt", ms=0.0, ok=False, filename=file.filename or "", error=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
