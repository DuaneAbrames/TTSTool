from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Optional

import edge_tts


async def synthesize_stream(
    text: str,
    voice: str,
    audio_format: Optional[str] = None,
) -> AsyncGenerator[bytes, None]:
    """Yield audio bytes using edge-tts streaming API.

    edge-tts has had API differences across versions regarding how to specify
    the desired audio format. Some versions accept `output_format` on
    `Communicate.stream()`, others accept it (or `format`) on the constructor,
    and older ones don't support overriding format at all.

    To be robust, we attempt a few strategies and gracefully fall back to the
    library defaults if the current version doesn't support our requested
    format, avoiding hard failures like "unexpected keyword argument".
    """

    communicator = edge_tts.Communicate(text, voice=voice)

    # Try multiple ways to provide the format, catching TypeError for
    # unsupported keyword arguments across versions.
    async def _get_stream_gen():
        if not audio_format:
            return communicator.stream()

        # 1) Preferred on newer releases: pass on stream()
        try:
            return communicator.stream(output_format=audio_format)
        except TypeError:
            pass

        # 2) Some releases used `format` kw on stream()
        try:
            return communicator.stream(format=audio_format)  # type: ignore[arg-type]
        except TypeError:
            pass

        # 3) Try on constructor with `output_format`
        try:
            comm2 = edge_tts.Communicate(text, voice=voice, output_format=audio_format)
            return comm2.stream()
        except TypeError:
            pass

        # 4) Try on constructor with `format`
        try:
            comm3 = edge_tts.Communicate(text, voice=voice, format=audio_format)  # type: ignore[arg-type]
            return comm3.stream()
        except TypeError:
            pass

        # 5) Final fallback: use defaults
        return communicator.stream()

    gen = await _get_stream_gen()

    async for chunk in gen:
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
