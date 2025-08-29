from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Optional

import edge_tts


async def synthesize_stream(
    text: str,
    voice: str,
    audio_format: Optional[str] = None,
) -> AsyncGenerator[bytes, None]:
    """Yield audio bytes using edge-tts streaming API."""
    communicator = edge_tts.Communicate(text, voice=voice)

    stream_kwargs = {}
    if audio_format:
        # edge-tts expects output_format on stream(), not on constructor
        stream_kwargs["output_format"] = audio_format

    async for chunk in communicator.stream(**stream_kwargs):
        if chunk["type"] == "audio":
            yield chunk["data"]
        elif chunk["type"] == "sentence_boundary":
            # allow event loop to breathe on long texts
            await asyncio.sleep(0)


def guess_mime_from_format(audio_format: str | None) -> str:
    if not audio_format:
        return "audio/mpeg"
    fmt = audio_format.lower()
    if "mp3" in fmt:
        return "audio/mpeg"
    if "wav" in fmt or "pcm" in fmt:
        return "audio/wav"
    if "ogg" in fmt:
        return "audio/ogg"
    if "webm" in fmt:
        return "audio/webm"
    return "application/octet-stream"
