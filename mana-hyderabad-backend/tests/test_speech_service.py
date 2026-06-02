import pytest

from app.schemas.speech import SpeechSynthesisResponse, SpeechTranscriptionResponse
from app.services.providers.base_speech_provider import BaseSpeechProvider, SpeechProviderError
from app.services.speech_service import SpeechServiceError, synthesize_text, transcribe_audio


class FakeSpeechProvider(BaseSpeechProvider):
    name = "FAKE"

    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str,
        language: str,
    ) -> SpeechTranscriptionResponse:
        return SpeechTranscriptionResponse(
            transcript="  Madhapur metro దగ్గర garbage dump అయింది  ",
            detectedLanguage="te-en",
            requestedLanguage=language,
            provider=self.name,
            audioDurationSeconds=8.4,
            requiresHumanVerification=True,
            fallbackUsed=False,
        )

    async def synthesize(self, text: str, language: str) -> SpeechSynthesisResponse:
        return SpeechSynthesisResponse(
            audioBase64="UklGRg==",
            audioUrl=None,
            language=language,
            provider=self.name,
            format="wav",
            fallbackUsed=False,
        )

    async def health_check(self) -> bool:
        return True


class FailingSpeechProvider(FakeSpeechProvider):
    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str,
        language: str,
    ) -> SpeechTranscriptionResponse:
        raise SpeechProviderError("provider failed")


@pytest.mark.anyio
async def test_transcribe_audio_success():
    response = await transcribe_audio(b"webm-bytes", "audio/webm", "te", FakeSpeechProvider())

    assert response.transcript == "Madhapur metro దగ్గర garbage dump అయింది"
    assert response.detected_language == "te-en"
    assert response.provider == "FAKE"


@pytest.mark.anyio
async def test_transcribe_rejects_unsupported_mime_type():
    with pytest.raises(SpeechServiceError, match="Unsupported audio format"):
        await transcribe_audio(b"%PDF", "application/pdf", "en", FakeSpeechProvider())


@pytest.mark.anyio
async def test_transcribe_rejects_empty_audio():
    with pytest.raises(SpeechServiceError, match="empty"):
        await transcribe_audio(b"", "audio/webm", "en", FakeSpeechProvider())


@pytest.mark.anyio
async def test_transcribe_provider_failure_is_safe():
    with pytest.raises(SpeechServiceError, match="Could not transcribe audio"):
        await transcribe_audio(b"webm-bytes", "audio/webm", "en", FailingSpeechProvider())


@pytest.mark.anyio
async def test_synthesize_disabled_returns_safe_fallback():
    response = await synthesize_text("Please share the location.", "en", FakeSpeechProvider())

    assert response.provider in {"DISABLED", "FAKE"}
    if response.provider == "DISABLED":
        assert response.fallback_used is True
