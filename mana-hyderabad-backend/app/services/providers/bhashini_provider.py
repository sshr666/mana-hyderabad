import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.translation import TranslationResponse
from app.services.providers.base_translation_provider import (
    BaseTranslationProvider,
    TranslationProviderError,
    UnsupportedLanguagePairError,
)


@dataclass
class BhashiniPipelineConfig:
    service_id: str
    callback_url: str
    auth_header_name: str
    auth_header_value: str
    expires_at: float


class BhashiniTranslationProvider(BaseTranslationProvider):
    name = "BHASHINI"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, BhashiniPipelineConfig] = {}

    async def health_check(self) -> bool:
        return bool(
            self.settings.bhashini_user_id
            and self.settings.bhashini_api_key
            and self.settings.bhashini_pipeline_id
            and self.settings.bhashini_config_url
        )

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        preserve_terms: list[str] | None = None,
    ) -> TranslationResponse:
        if not await self.health_check():
            raise TranslationProviderError("BHASHINI credentials are not configured.")
        if source_language == target_language:
            return TranslationResponse(
                originalText=text,
                translatedText=text,
                sourceLanguage=source_language,
                targetLanguage=target_language,
                detectedLanguage=source_language,
                isMixedLanguage=False,
                provider="NO_TRANSLATION_REQUIRED",
                preservedTerms=preserve_terms or [],
                requiresHumanVerification=False,
            )

        config = await self._get_pipeline_config(source_language, target_language)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {"sourceLanguage": source_language, "targetLanguage": target_language},
                        "serviceId": config.service_id,
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        headers = {config.auth_header_name: config.auth_header_value}
        try:
            data = await self._post_json(config.callback_url, payload, headers)
        except TranslationProviderError:
            self._cache.pop(_cache_key(source_language, target_language), None)
            raise

        translated = _extract_translated_text(data)
        if not translated:
            raise TranslationProviderError("BHASHINI returned an empty translation.")
        return TranslationResponse(
            originalText=text,
            translatedText=translated,
            sourceLanguage=source_language,
            targetLanguage=target_language,
            detectedLanguage=source_language,
            isMixedLanguage="-" in source_language,
            provider=self.name,
            preservedTerms=preserve_terms or [],
            requiresHumanVerification=True,
        )

    async def _get_pipeline_config(self, source_language: str, target_language: str) -> BhashiniPipelineConfig:
        key = _cache_key(source_language, target_language)
        cached = self._cache.get(key)
        if cached and cached.expires_at > time.time():
            return cached

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {"language": {"sourceLanguage": source_language, "targetLanguage": target_language}},
                }
            ],
            "pipelineRequestConfig": {"pipelineId": self.settings.bhashini_pipeline_id},
        }
        headers = {
            "userID": self.settings.bhashini_user_id,
            "ulcaApiKey": self.settings.bhashini_api_key,
        }
        data = await self._post_json(self.settings.bhashini_config_url, payload, headers)
        config = _parse_pipeline_config(data, source_language, target_language, self.settings.bhashini_cache_ttl_seconds)
        self._cache[key] = config
        return config

    async def _post_json(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.settings.translation_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.translation_timeout_seconds) as client:
                    response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 429:
                    raise TranslationProviderError("Translation provider rate limit reached.")
                if response.status_code >= 500:
                    raise TranslationProviderError("Translation provider is temporarily unavailable.")
                if response.status_code >= 400:
                    raise UnsupportedLanguagePairError("Translation language pair is not supported.")
                data = response.json()
                if not isinstance(data, dict):
                    raise TranslationProviderError("Translation provider returned malformed data.")
                return data
            except (httpx.TimeoutException, httpx.TransportError, ValueError, TranslationProviderError) as error:
                last_error = error
                if attempt >= self.settings.translation_max_retries:
                    break
        raise TranslationProviderError("Translation provider request failed.") from last_error


def _cache_key(source_language: str, target_language: str) -> str:
    return f"{source_language}:{target_language}"


def _parse_pipeline_config(
    data: dict[str, Any],
    source_language: str,
    target_language: str,
    ttl_seconds: int,
) -> BhashiniPipelineConfig:
    try:
        pipeline = data["pipelineResponseConfig"][0]
        service = pipeline["config"][0]
        service_id = service["serviceId"]
        callback_url = data["pipelineInferenceAPIEndPoint"]["callbackUrl"]
        auth = data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]
        header_name = auth["name"]
        header_value = auth["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise TranslationProviderError("BHASHINI pipeline configuration was malformed.") from error

    language = service.get("language", {})
    if language and (
        language.get("sourceLanguage") not in {source_language, None}
        or language.get("targetLanguage") not in {target_language, None}
    ):
        raise UnsupportedLanguagePairError("BHASHINI returned a different language pair.")

    return BhashiniPipelineConfig(
        service_id=service_id,
        callback_url=callback_url,
        auth_header_name=header_name,
        auth_header_value=header_value,
        expires_at=time.time() + ttl_seconds,
    )


def _extract_translated_text(data: dict[str, Any]) -> str | None:
    candidates = [
        ("pipelineResponse", 0, "output", 0, "target"),
        ("pipelineResponse", 0, "output", 0, "targetText"),
        ("output", 0, "target"),
        ("output", 0, "targetText"),
    ]
    for path in candidates:
        value: Any = data
        try:
            for part in path:
                value = value[part]
            if isinstance(value, str):
                return value.strip()
        except (KeyError, IndexError, TypeError):
            continue
    return None
