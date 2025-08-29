from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .stt_base import STTEngine, STTError


@dataclass
class AzureSTT(STTEngine):
    subscription_key: str
    region: str
    language: str = "en-US"

    async def transcribe(self, file_path: str) -> str:
        try:
            import azure.cognitiveservices.speech as speechsdk
        except Exception as exc:  # pragma: no cover - import guard
            raise STTError(
                "azure-cognitiveservices-speech not installed. Install requirements-stt-azure.txt"
            ) from exc

        def _run_blocking() -> str:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, region=self.region
            )
            speech_config.speech_recognition_language = self.language
            audio_config = speechsdk.audio.AudioConfig(filename=file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )
            result = recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise STTError("Azure STT: No speech could be recognized.")
            else:
                details = result.cancellation_details if hasattr(result, 'cancellation_details') else None
                message = getattr(details, 'reason', 'Unknown cancellation') if details else 'Unknown error'
                raise STTError(f"Azure STT error: {message}")

        return await asyncio.to_thread(_run_blocking)

