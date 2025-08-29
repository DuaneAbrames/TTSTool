Param(
  [ValidateSet('none','azure','whisper','both')]
  [string]$Provider = 'none'
)

$ErrorActionPreference = 'Stop'

Write-Host "[setup] Creating venv (.venv) if missing…"
if (-not (Test-Path -Path .venv)) {
  python -m venv .venv
}

$python = Join-Path -Path .venv -ChildPath 'Scripts/python.exe'
if (-not (Test-Path -Path $python)) {
  throw "Python not found in .venv. Ensure Python is installed and try again."
}

Write-Host "[setup] Upgrading pip…"
& $python -m pip install --upgrade pip

Write-Host "[setup] Installing base requirements (FastAPI, edge-tts)…"
& $python -m pip install -r requirements.txt

switch ($Provider) {
  'azure'   { Write-Host "[setup] Installing Azure STT deps…"; & $python -m pip install -r requirements-stt-azure.txt }
  'whisper' { Write-Host "[setup] Installing Whisper STT deps…"; & $python -m pip install -r requirements-stt-whisper.txt }
  'both'    { Write-Host "[setup] Installing Azure + Whisper STT deps…"; & $python -m pip install -r requirements-stt-azure.txt; & $python -m pip install -r requirements-stt-whisper.txt }
  default   { }
}

if ($Provider -in @('whisper','both')) {
  $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
  if (-not $ffmpeg) {
    Write-Warning "ffmpeg not found. Whisper requires ffmpeg. Install via 'choco install ffmpeg' or your package manager."
  }
}

Write-Host "[setup] Done. Next steps:"
Write-Host "  1) Activate venv: .\\.venv\\Scripts\\Activate.ps1"
Write-Host "  2) Run server:   uvicorn app.main:app --reload --port 8000"
Write-Host "  3) Open UI:      http://localhost:8000/ui (Status: /status)"

