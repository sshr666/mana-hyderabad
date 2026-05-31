from fastapi import APIRouter

from app.schemas.translation import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.language_detection_service import detect_language
from app.services.translation_service import translate_text

router = APIRouter(prefix="/api/translation", tags=["translation"])


@router.post("/detect-language", response_model=DetectLanguageResponse)
def detect_language_endpoint(payload: DetectLanguageRequest) -> DetectLanguageResponse:
    return detect_language(payload.text)


@router.post("/translate", response_model=TranslationResponse)
async def translate_endpoint(payload: TranslationRequest) -> TranslationResponse:
    return await translate_text(
        payload.text,
        payload.source_language,
        payload.target_language,
        payload.preserve_terms,
    )
