from fastapi.testclient import TestClient

from app.main import app
from app.schemas.speech import SpeechSynthesisResponse, SpeechTranscriptionResponse
from app.services.speech_service import SpeechServiceError


client = TestClient(app)


def test_transcribe_endpoint_returns_transcript(monkeypatch):
    async def fake_transcribe_audio(audio_bytes: bytes, mime_type: str, language: str):
        assert audio_bytes == b"fake-webm"
        assert mime_type == "audio/webm"
        return SpeechTranscriptionResponse(
            transcript="Road pe waterlogging hai near Gachibowli signal",
            detectedLanguage="hi-en",
            requestedLanguage=language,
            provider="BHASHINI",
            audioDurationSeconds=5.0,
            requiresHumanVerification=True,
            fallbackUsed=False,
        )

    monkeypatch.setattr("app.api.speech.transcribe_audio", fake_transcribe_audio)

    response = client.post(
        "/api/speech/transcribe",
        files={"file": ("complaint.webm", b"fake-webm", "audio/webm")},
        data={"language": "hi"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == "Road pe waterlogging hai near Gachibowli signal"
    assert body["requestedLanguage"] == "hi"
    assert body["provider"] == "BHASHINI"


def test_transcribe_endpoint_returns_safe_error(monkeypatch):
    async def fake_transcribe_audio(audio_bytes: bytes, mime_type: str, language: str):
        raise SpeechServiceError("Could not transcribe audio. You can type manually.")

    monkeypatch.setattr("app.api.speech.transcribe_audio", fake_transcribe_audio)

    response = client.post(
        "/api/speech/transcribe",
        files={"file": ("complaint.pdf", b"%PDF", "application/pdf")},
        data={"language": "en"},
    )

    assert response.status_code == 422
    assert "Could not transcribe audio" in response.json()["detail"]


def test_synthesize_endpoint_returns_disabled_fallback(monkeypatch):
    async def fake_synthesize_text(text: str, language: str):
        return SpeechSynthesisResponse(
            audioBase64=None,
            audioUrl=None,
            language=language,
            provider="DISABLED",
            format="none",
            fallbackUsed=True,
        )

    monkeypatch.setattr("app.api.speech.synthesize_text", fake_synthesize_text)

    response = client.post(
        "/api/speech/synthesize",
        json={"text": "Please share the exact location.", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "DISABLED"
    assert body["fallbackUsed"] is True


def test_synthesize_endpoint_rejects_empty_text():
    response = client.post("/api/speech/synthesize", json={"text": "   ", "language": "en"})

    assert response.status_code == 422
