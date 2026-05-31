from app.config import get_settings
from app.schemas.translation import NormalizedComplaintText, TranslationResponse
from app.services.language_detection_service import detect_language
from app.services.locality_preservation_service import protect_locality_terms, restore_locality_terms
from app.services.providers.base_translation_provider import TranslationProviderError
from app.services.providers.bhashini_provider import BhashiniTranslationProvider
from app.services.providers.indictrans2_provider import IndicTrans2Provider


SUPPORTED_LANGUAGES = {"en", "te", "hi", "ur"}

STATIC_REPLY_TRANSLATIONS = {
    ("Please share the exact location or select it on the map.", "te"): "దయచేసి ఖచ్చితమైన ప్రదేశాన్ని షేర్ చేయండి లేదా మ్యాప్‌లో ఎంచుకోండి.",
    ("Please share the exact location or select it on the map.", "hi"): "कृपया सही स्थान साझा करें या मानचित्र पर चुनें।",
    ("Please share the exact location or select it on the map.", "ur"): "براہ کرم درست مقام شیئر کریں یا نقشے پر منتخب کریں۔",
    ("Please share the exact location so the issue can be reported accurately.", "te"): "సమస్యను ఖచ్చితంగా నమోదు చేయడానికి దయచేసి ఖచ్చితమైన ప్రదేశాన్ని షేర్ చేయండి.",
    ("Please share the exact location so the issue can be reported accurately.", "hi"): "समस्या को सही तरीके से दर्ज करने के लिए कृपया सही स्थान साझा करें।",
    ("Please share the exact location so the issue can be reported accurately.", "ur"): "درخواست کو درست طریقے سے درج کرنے کے لیے براہ کرم درست مقام شیئر کریں۔",
}

RULE_TRANSLATIONS = [
    (
        ["garbage", "dump", "చెత్త", "కచరా", "کچرا"],
        "Garbage has accumulated near {place}.",
        "Garbage has accumulated.",
    ),
    (
        ["waterlogging", "పانی", "पानी", "water", "flood"],
        "There is waterlogging near {place}.",
        "There is waterlogging.",
    ),
    (
        ["drain", "నాలా", "नाला", "نالہ", "ayindi"],
        "The drain is blocked near {place}.",
        "The drain is blocked.",
    ),
    (
        ["pothole", "గుంత", "गड्ढा", "گڑھا"],
        "There is a pothole near {place}.",
        "There is a pothole.",
    ),
    (
        ["street light", "light", "kaam nahi", "వీధి దీపం"],
        "A street light is not working near {place}.",
        "A street light is not working.",
    ),
]


async def translate_text(
    text: str,
    source_language: str | None,
    target_language: str,
    preserve_terms: list[str] | None = None,
) -> TranslationResponse:
    clean_text = text.strip()
    detected = detect_language(clean_text, source_language)
    source = _base_language(source_language or detected.detected_language)
    target = _base_language(target_language)
    protected = protect_locality_terms(clean_text, preserve_terms)

    if source == target == "en" and detected.detected_language == "en":
        return TranslationResponse(
            originalText=clean_text,
            translatedText=clean_text,
            sourceLanguage="en",
            targetLanguage="en",
            detectedLanguage=detected.detected_language,
            isMixedLanguage=False,
            provider="NO_TRANSLATION_REQUIRED",
            preservedTerms=protected.preserved_terms,
            requiresHumanVerification=False,
        )

    if not get_settings().enable_translation:
        return _fallback_translation(clean_text, protected, source, target, detected.detected_language)
    if source == "unknown" or target == "unknown":
        return _fallback_translation(clean_text, protected, source, target, detected.detected_language)

    providers = [BhashiniTranslationProvider()]
    if get_settings().enable_indic_trans2_fallback:
        providers.append(IndicTrans2Provider())

    for provider in providers:
        try:
            response = await provider.translate(
                protected.text,
                source,
                target,
                protected.preserved_terms,
            )
            restored = restore_locality_terms(response.translated_text, protected)
            if restored and not _contains_placeholder(restored):
                return response.model_copy(
                    update={
                        "translated_text": restored,
                        "original_text": clean_text,
                        "detected_language": detected.detected_language,
                        "is_mixed_language": detected.is_mixed_language,
                        "preserved_terms": protected.preserved_terms,
                    }
                )
        except TranslationProviderError:
            continue

    return _fallback_translation(clean_text, protected, source, target, detected.detected_language)


async def normalize_complaint_to_english(
    text: str,
    selected_language: str | None = None,
) -> NormalizedComplaintText:
    detected = detect_language(text, selected_language)
    response = await translate_text(text, selected_language or detected.detected_language, "en")
    return NormalizedComplaintText(
        originalText=text.strip(),
        originalLanguage=_base_language(selected_language or detected.detected_language),
        detectedLanguage=detected.detected_language,
        normalizedEnglishText=response.translated_text,
        isMixedLanguage=detected.is_mixed_language,
        provider=response.provider,
        requiresHumanVerification=response.requires_human_verification,
    )


async def translate_citizen_reply(text: str, target_language: str) -> TranslationResponse:
    target = _base_language(target_language)
    if target == "en":
        return TranslationResponse(
            originalText=text,
            translatedText=text,
            sourceLanguage="en",
            targetLanguage="en",
            detectedLanguage="en",
            isMixedLanguage=False,
            provider="NO_TRANSLATION_REQUIRED",
            preservedTerms=[],
            requiresHumanVerification=False,
        )
    translated = STATIC_REPLY_TRANSLATIONS.get((text, target))
    if translated:
        return TranslationResponse(
            originalText=text,
            translatedText=translated,
            sourceLanguage="en",
            targetLanguage=target,
            detectedLanguage="en",
            isMixedLanguage=False,
            provider="FALLBACK_STATIC",
            preservedTerms=[],
            requiresHumanVerification=True,
        )
    return await translate_text(text, "en", target)


def _fallback_translation(
    original_text: str,
    protected,
    source_language: str,
    target_language: str,
    detected_language: str,
) -> TranslationResponse:
    translated = _rule_based_translation(original_text, protected, target_language)
    return TranslationResponse(
        originalText=original_text,
        translatedText=translated,
        sourceLanguage=source_language,
        targetLanguage=target_language,
        detectedLanguage=detected_language,
        isMixedLanguage="-" in detected_language,
        provider="FALLBACK",
        preservedTerms=protected.preserved_terms,
        requiresHumanVerification=True,
    )


def _rule_based_translation(original_text: str, protected, target_language: str) -> str:
    if target_language != "en":
        return original_text
    lower = original_text.lower()
    place = protected.preserved_terms[0] if protected.preserved_terms else None
    for keywords, with_place, without_place in RULE_TRANSLATIONS:
        if any(keyword.lower() in lower for keyword in keywords):
            return with_place.format(place=place) if place else without_place
    return restore_locality_terms(protected.text, protected)


def _base_language(language: str | None) -> str:
    if not language:
        return "unknown"
    if language.startswith("te"):
        return "te"
    if language.startswith("hi"):
        return "hi"
    if language.startswith("ur"):
        return "ur"
    if language.startswith("en"):
        return "en"
    return language if language in SUPPORTED_LANGUAGES else "unknown"


def _contains_placeholder(text: str) -> bool:
    return "__PLACE_" in text
