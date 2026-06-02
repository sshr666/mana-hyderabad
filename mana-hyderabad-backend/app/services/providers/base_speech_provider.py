from abc import ABC, abstractmethod

from app.schemas.speech import SpeechSynthesisResponse, SpeechTranscriptionResponse


class SpeechProviderError(RuntimeError):
    """Raised when a speech provider cannot return a usable result."""


class UnsupportedSpeechLanguageError(SpeechProviderError):
    """Raised when a speech provider does not support the requested language."""


class BaseSpeechProvider(ABC):
    name: str

    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str,
        language: str,
    ) -> SpeechTranscriptionResponse:
        ...

    @abstractmethod
    async def synthesize(self, text: str, language: str) -> SpeechSynthesisResponse:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
