from abc import ABC, abstractmethod

from app.schemas.translation import TranslationResponse


class TranslationProviderError(RuntimeError):
    """Raised when a translation provider cannot return a trusted translation."""


class UnsupportedLanguagePairError(TranslationProviderError):
    """Raised when a provider does not support the requested source-target pair."""


class BaseTranslationProvider(ABC):
    name: str

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        preserve_terms: list[str] | None = None,
    ) -> TranslationResponse:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
