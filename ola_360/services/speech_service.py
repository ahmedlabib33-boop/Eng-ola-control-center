from __future__ import annotations

import os
from pathlib import Path

import requests


class SpeechToTextService:
    """Transcribe audio with a real provider when configured."""

    def __init__(self, provider: str | None = None):
        self.provider = (provider or os.getenv("OLA_STT_PROVIDER") or "openai").lower()

    def transcribe_file(self, audio_path: str) -> dict[str, str]:
        path = Path(audio_path)
        if not path.exists() or not path.is_file():
            raise ValueError("Audio file was not found.")
        if self.provider == "openai":
            return self._openai(path)
        raise ValueError(f"Unsupported speech-to-text provider: {self.provider}")

    def status(self) -> str:
        if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
            return "OpenAI speech-to-text is configured."
        return "Speech-to-text is not configured. Set OPENAI_API_KEY to transcribe audio files."

    def _openai(self, path: Path) -> dict[str, str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for real speech-to-text transcription.")
        with path.open("rb") as handle:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={"model": os.getenv("OLA_STT_MODEL", "whisper-1")},
                files={"file": (path.name, handle)},
                timeout=120,
            )
        if response.status_code >= 400:
            raise ValueError(f"Speech-to-text failed: {response.status_code} {response.text[:500]}")
        payload = response.json()
        transcript = str(payload.get("text", "")).strip()
        if not transcript:
            raise ValueError("Speech-to-text provider returned an empty transcript.")
        return {
            "provider": "openai",
            "source_path": str(path),
            "transcript": transcript,
            "confidence": "Provider transcript preserved verbatim.",
        }
