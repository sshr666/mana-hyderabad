import httpx

from app.config import get_settings
from app.schemas.translation import TranslationResponse
from app.services.providers.base_translation_provider import BaseTranslationProvider, TranslationProviderError


class IndicTrans2Provider(BaseTranslationProvider):
    name = "INDIC_TRANS2"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def health_check(self) -> bool:
        return bool(self.settings.enable_indic_trans2_fallback and self.settings.indic_trans2_base_url)

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        preserve_terms: list[str] | None = None,
    ) -> TranslationResponse:
        if not await self.health_check():
            raise TranslationProviderError("IndicTrans2 fallback is not configured.")
        payload = {
            "text": text,
            "sourceLanguage": source_language,
            "targetLanguage": target_language,
            "preserveTerms": preserve_terms or [],
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.indic_trans2_timeout_seconds) as client:
                response = await client.post(f"{self.settings.indic_trans2_base_url.rstrip('/')}/translate", json=payload)
            response.raise_for_status()
            data = response.json()
            translated = data.get("translatedText") or data.get("translation")
        except (httpx.HTTPError, ValueError, AttributeError) as error:
            raise TranslationProviderError("IndicTrans2 request failed.") from error
        if not isinstance(translated, str) or not translated.strip():
            raise TranslationProviderError("IndicTrans2 returned an empty translation.")
        return TranslationResponse(
            originalText=text,
            translatedText=translated.strip(),
            sourceLanguage=source_language,
            targetLanguage=target_language,
            detectedLanguage=source_language,
            isMixedLanguage="-" in source_language,
            provider=self.name,
            preservedTerms=preserve_terms or [],
            requiresHumanVerification=True,
        )
