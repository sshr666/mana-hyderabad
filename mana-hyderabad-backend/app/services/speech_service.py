from app.config import get_settings
from app.schemas.speech import SpeechSynthesisResponse, SpeechTranscriptionResponse
from app.services.providers.base_speech_provider import BaseSpeechProvider, SpeechProviderError
from app.services.providers.bhashini_speech_provider import BhashiniSpeechProvider


SUPPORTED_SPEECH_LANGUAGES = {"en", "te", "hi", "ur"}


class SpeechServiceError(RuntimeError):
    """Safe speech-service error suitable for API responses."""


async def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str,
    language: str,
    provider: BaseSpeechProvider | None = None,
) -> SpeechTranscriptionResponse:
    settings = get_settings()
    if not settings.enable_speech_input:
        raise SpeechServiceError("Speech input is currently disabled.")
    _validate_language(language)
    _validate_audio(audio_bytes, mime_type)

    speech_provider = provider or BhashiniSpeechProvider()
    try:
        response = await speech_provider.transcribe(audio_bytes, mime_type, language)
    except SpeechProviderError as error:
        raise SpeechServiceError(
            "Could not transcribe audio. You can type or edit your complaint manually."
        ) from error

    transcript = _normalize_transcript(response.transcript)
    if not transcript:
        raise SpeechServiceError("Could not transcribe audio. You can type your complaint manually.")
    return response.model_copy(update={"transcript": transcript})


async def synthesize_text(
    text: str,
    language: str,
    provider: BaseSpeechProvider | None = None,
) -> SpeechSynthesisResponse:
    settings = get_settings()
    _validate_language(language)
    clean_text = text.strip()
    if not clean_text:
        raise SpeechServiceError("Text is required for spoken response.")
    if len(clean_text) > 1000:
        raise SpeechServiceError("Spoken response text is too long.")
    if not settings.enable_tts_responses:
        return SpeechSynthesisResponse(
            audioBase64=None,
            audioUrl=None,
            language=language,
            provider="DISABLED",
            format="none",
            fallbackUsed=True,
        )

    speech_provider = provider or BhashiniSpeechProvider()
    try:
        return await speech_provider.synthesize(clean_text, language)
    except SpeechProviderError as error:
        raise SpeechServiceError("Spoken response is unavailable right now.") from error


def _validate_audio(audio_bytes: bytes, mime_type: str) -> None:
    settings = get_settings()
    if not audio_bytes:
        raise SpeechServiceError("Audio recording is empty.")
    base_mime = mime_type.split(";")[0].strip().lower()
    if base_mime not in settings.allowed_audio_mime_types:
        raise SpeechServiceError(
            "Unsupported audio format. Record again or upload WEBM, WAV, MP3, MP4, or OGG audio."
        )
    if len(audio_bytes) > settings.max_audio_size_bytes:
        raise SpeechServiceError("Audio recording is too large. Please record a shorter complaint.")


def _validate_language(language: str) -> None:
    if language not in SUPPORTED_SPEECH_LANGUAGES:
        raise SpeechServiceError("Speech input supports English, Telugu, Hindi, and Urdu for now.")


def _normalize_transcript(transcript: str) -> str:
    return " ".join(transcript.strip().split())
