from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .stt_base import STTEngine, STTError


@dataclass
class WhisperSTT(STTEngine):
    model_name: str = "base"
    device: str = "cpu"

    async def transcribe(self, file_path: str) -> str:
        try:
            import whisper  # type: ignore
        except Exception as exc:  # pragma: no cover - import guard
            raise STTError(
                "openai-whisper not installed. Install requirements-stt-whisper.txt"
            ) from exc

        def _run_blocking() -> str:
            model = whisper.load_model(self.model_name, device=self.device)
            result = model.transcribe(file_path)
            return (result or {}).get("text", "").strip()

        return await asyncio.to_thread(_run_blocking)

