from __future__ import annotations

import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import get_settings
from app.services.tts_edge import synthesize_stream, guess_mime_from_format
from app.metrics import metrics


router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    audio_format: str | None = None


@router.post("", summary="Convert text to speech")
async def text_to_speech(payload: TTSRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="'text' is required")

    settings = get_settings()
    voice = payload.voice or settings.tts_default_voice
    audio_format = payload.audio_format or settings.tts_audio_format

    base_gen = synthesize_stream(payload.text, voice=voice, audio_format=audio_format)
    # Wrap to measure elapsed time and record metrics once streaming completes
    async def measured_gen():
        start = time.perf_counter()
        ok = True
        try:
            async for chunk in base_gen:
                yield chunk
        except Exception:
            ok = False
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            metrics.record(
                op="tts",
                ms=elapsed_ms,
                ok=ok,
                chars=len(payload.text),
                voice=voice,
                audio_format=audio_format,
            )
    media_type = guess_mime_from_format(audio_format)
    return StreamingResponse(measured_gen(), media_type=media_type)
