# TTSTool (FastAPI)

A simple FastAPI service that exposes two endpoints:

- Text to Speech (TTS) using edge-tts
- Speech to Text (STT) via pluggable engines (Azure Cognitive Services or OpenAI Whisper)

This is a minimal framework you can extend, with clear configuration and setup options.

## Features

- `POST /tts`: Convert text to speech using Microsoft Edge voices
- `POST /stt`: Upload audio (`.wav`, `.mp3`, etc.) and receive transcribed text
- Swappable STT providers: `azure` or `whisper`
- Environment-based config with sensible defaults

## Project Structure

- `app/main.py`: FastAPI application entry
- `app/config.py`: Pydantic settings and defaults
- `app/routers/tts.py`: TTS API route (edge-tts)
- `app/routers/stt.py`: STT API route (provider-agnostic)
- `app/services/tts_edge.py`: edge-tts streaming
- `app/services/stt_base.py`: STT interface and factory
- `app/services/stt_azure.py`: Azure Speech STT implementation
- `app/services/stt_whisper.py`: Whisper STT implementation
- `requirements.txt`: core dependencies
- `requirements-stt-azure.txt`: Azure STT dependency
- `requirements-stt-whisper.txt`: Whisper STT dependencies

## Prerequisites

- Python 3.11+ recommended
- For Whisper: `ffmpeg` installed on your system; models download on first use
- For Azure: valid Speech resource key and region

## Create and Activate a Virtual Environment

Windows (PowerShell):

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

Core (FastAPI + edge-tts):

```bash
pip install -r requirements.txt
```

Choose ONE STT provider (or install both):

Azure STT:

```bash
pip install -r requirements-stt-azure.txt
```

Whisper STT:

```bash
pip install -r requirements-stt-whisper.txt
```

Note: Whisper requires `ffmpeg` installed (e.g., `choco install ffmpeg` on Windows; `brew install ffmpeg` on macOS; `sudo apt install ffmpeg` on Ubuntu).

## Configure Environment

Create a `.env` file in the project root to set your preferences. Examples:

Azure STT (recommended for easy starters if you have Azure key):

```
stt_provider=azure
azure_speech_key=YOUR_AZURE_SPEECH_KEY
azure_speech_region=YOUR_AZURE_REGION   # e.g., eastus
azure_speech_language=en-US

# TTS defaults
tts_default_voice=en-US-AriaNeural
tts_audio_format=audio-24khz-48kbitrate-mono-mp3
```

Whisper STT:

```
stt_provider=whisper
whisper_model=base      # tiny|base|small|medium|large
whisper_device=cpu      # or cuda if you have GPU

# TTS defaults
tts_default_voice=en-US-AriaNeural
tts_audio_format=audio-24khz-48kbitrate-mono-mp3
```

If no STT provider is configured, `/stt` returns a helpful 400 error.

## Run the Server

From the repo root:

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000` for a small info payload. Web UI at `http://localhost:8000/ui`. Status page at `http://localhost:8000/status`. Interactive docs at `http://localhost:8000/docs`.

## API Examples

TTS (edge-tts):

```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from edge TTS!", "voice": "en-US-AriaNeural"}' \
  --output output.mp3
```

- Response is a streamed audio file. If you omit `voice`, the default from `.env` is used.
- To change encoding, set `audio_format` (e.g., `audio-24khz-48kbitrate-mono-mp3`, `riff-24khz-16bit-mono-pcm`).

STT (upload `.wav`/`.mp3`):

```bash
curl -X POST "http://localhost:8000/stt?provider=azure" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.wav" 
```

- If you omit `provider`, the service uses the `.env` `stt_provider`.

Example STT response:

```json
{
  "provider": "azure",
  "text": "This is a test."
}
```

## Notes

- edge-tts uses Microsoft Edge TTS voices and requires internet access at runtime.
- Azure STT recognizes short files easily with the current configuration. For lengthy audio, you may want to extend the Azure implementation to use continuous recognition.
- Whisper runs locally but downloads a model on first use and needs `ffmpeg`.

## PowerShell Setup Script (Windows)

Run the bundled script to create the venv and install dependencies:

```pwsh
./setup.ps1 -Provider azure     # or whisper, both, none
```

Then activate and run:

```pwsh
./.venv/Scripts/Activate.ps1
uvicorn app.main:app --reload --port 8000
```

## Next Steps (optional)

- Persist synthesized audio to storage (S3, disk) with IDs
- Add language selection on `/tts` and `/stt`
- Add auth (API keys/JWT) and request limits
- Add Dockerfile and CI
