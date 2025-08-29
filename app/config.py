from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='')

    app_name: str = Field(default="TTSTool")

    # TTS (edge-tts)
    tts_default_voice: str = Field(default="en-US-AriaNeural")
    tts_audio_format: str = Field(default="audio-24khz-48kbitrate-mono-mp3")

    # STT provider: 'azure', 'whisper', or 'none'
    stt_provider: str = Field(default="none")

    # Azure Speech (if using 'azure')
    azure_speech_key: str | None = None
    azure_speech_region: str | None = None
    azure_speech_language: str = Field(default="en-US")

    # Whisper (if using 'whisper')
    whisper_model: str = Field(default="base")  # tiny|base|small|medium|large
    whisper_device: str = Field(default="cpu")   # cpu|cuda


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

