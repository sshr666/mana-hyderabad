from __future__ import annotations

import base64
import json
from pathlib import Path

import httpx


API_BASE_URL = "http://127.0.0.1:8000"
TEST_ASSET = Path("test-assets/sample-english.webm")


def main() -> None:
    if not TEST_ASSET.exists() or TEST_ASSET.stat().st_size == 0:
        print("Sample audio is not available. Add a short WEBM file at test-assets/sample-english.webm.")
        print("The unit tests mock BHASHINI ASR; this script is for manual provider verification.")
        return

    with httpx.Client(timeout=60) as client:
        with TEST_ASSET.open("rb") as audio_file:
            transcription = client.post(
                f"{API_BASE_URL}/api/speech/transcribe",
                data={"language": "en"},
                files={"file": ("sample-english.webm", audio_file, "audio/webm")},
            )
        transcription.raise_for_status()
        transcript_body = transcription.json()
        print("Transcript:")
        print(json.dumps(transcript_body, indent=2, ensure_ascii=False))

        transcript = transcript_body["transcript"]
        detection = client.post(
            f"{API_BASE_URL}/api/translation/detect-language",
            json={"text": transcript},
        )
        detection.raise_for_status()
        print("Language detection:")
        print(json.dumps(detection.json(), indent=2, ensure_ascii=False))

        analysis = client.post(
            f"{API_BASE_URL}/api/complaints/analyse",
            json={
                "text": transcript,
                "language": transcript_body["requestedLanguage"],
                "photoUrl": None,
                "latitude": None,
                "longitude": None,
                "landmark": None,
            },
        )
        analysis.raise_for_status()
        print("Complaint analysis:")
        print(json.dumps(analysis.json(), indent=2, ensure_ascii=False))

        tts = client.post(
            f"{API_BASE_URL}/api/speech/synthesize",
            json={"text": analysis.json().get("citizenReply") or "Please share the location.", "language": "en"},
        )
        tts.raise_for_status()
        tts_body = tts.json()
        if tts_body.get("audioBase64"):
            print(f"TTS returned {len(base64.b64decode(tts_body['audioBase64']))} audio bytes.")
        else:
            print("TTS fallback:", tts_body)

    print("Speech verification flow completed.")


if __name__ == "__main__":
    main()
