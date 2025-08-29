from __future__ import annotations

import abc
from typing import Optional

from app.config import Settings


class STTError(RuntimeError):
    pass


class STTEngine(abc.ABC):
    @abc.abstractmethod
    async def transcribe(self, file_path: str) -> str:
        """Return the transcription text for the given audio file path."""


def get_stt_engine(settings: Settings, provider_override: Optional[str] = None) -> STTEngine:
    provider = (provider_override or settings.stt_provider or "none").lower()
    if provider == "azure":
        from .stt_azure import AzureSTT

        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise STTError(
                "Azure STT not configured. Set 'azure_speech_key' and 'azure_speech_region'."
            )
        return AzureSTT(
            subscription_key=settings.azure_speech_key,
            region=settings.azure_speech_region,
            language=settings.azure_speech_language,
        )
    elif provider == "whisper":
        from .stt_whisper import WhisperSTT

        return WhisperSTT(model_name=settings.whisper_model, device=settings.whisper_device)
    else:
        raise STTError(
            "No STT provider configured. Set 'stt_provider' to 'azure' or 'whisper'."
        )

