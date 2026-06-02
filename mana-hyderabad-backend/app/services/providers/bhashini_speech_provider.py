import base64
import time
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from app.config import get_settings
from app.schemas.speech import SpeechSynthesisResponse, SpeechTranscriptionResponse
from app.services.language_detection_service import detect_language
from app.services.providers.base_speech_provider import (
    BaseSpeechProvider,
    SpeechProviderError,
    UnsupportedSpeechLanguageError,
)

SpeechTask = Literal["asr", "tts"]


@dataclass
class BhashiniSpeechPipelineConfig:
    service_id: str
    callback_url: str
    auth_header_name: str
    auth_header_value: str
    expires_at: float


class BhashiniSpeechProvider(BaseSpeechProvider):
    name = "BHASHINI"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, BhashiniSpeechPipelineConfig] = {}

    async def health_check(self) -> bool:
        return bool(
            self.settings.bhashini_user_id
            and self.settings.bhashini_api_key
            and self.settings.bhashini_speech_config_url
        )

    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str,
        language: str,
    ) -> SpeechTranscriptionResponse:
        if not await self.health_check() or not self.settings.bhashini_asr_pipeline_id:
            raise SpeechProviderError("BHASHINI ASR is not configured.")

        config = await self._get_pipeline_config("asr", language)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "serviceId": config.service_id,
                        "audioFormat": _audio_format_from_mime(mime_type),
                    },
                }
            ],
            "inputData": {
                "audio": [{"audioContent": base64.b64encode(audio_bytes).decode("ascii")}]
            },
        }
        try:
            data = await self._post_json(config.callback_url, payload, {config.auth_header_name: config.auth_header_value})
        except SpeechProviderError:
            self._cache.pop(_cache_key("asr", language), None)
            raise

        transcript = _extract_transcript(data)
        if not transcript:
            raise SpeechProviderError("BHASHINI ASR returned an empty transcript.")
        detected = detect_language(transcript, language)
        return SpeechTranscriptionResponse(
            transcript=transcript,
            detectedLanguage=detected.detected_language,
            requestedLanguage=language,
            provider=self.name,
            audioDurationSeconds=None,
            requiresHumanVerification=True,
            fallbackUsed=False,
        )

    async def synthesize(self, text: str, language: str) -> SpeechSynthesisResponse:
        if not self.settings.enable_tts_responses:
            return SpeechSynthesisResponse(
                audioBase64=None,
                audioUrl=None,
                language=language,
                provider="DISABLED",
                format="none",
                fallbackUsed=True,
            )
        if not await self.health_check() or not self.settings.bhashini_tts_pipeline_id:
            raise SpeechProviderError("BHASHINI TTS is not configured.")

        config = await self._get_pipeline_config("tts", language)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {"sourceLanguage": language},
                        "serviceId": config.service_id,
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        try:
            data = await self._post_json(config.callback_url, payload, {config.auth_header_name: config.auth_header_value})
        except SpeechProviderError:
            self._cache.pop(_cache_key("tts", language), None)
            raise

        audio_base64 = _extract_audio_base64(data)
        if not audio_base64:
            raise SpeechProviderError("BHASHINI TTS returned no audio.")
        return SpeechSynthesisResponse(
            audioBase64=audio_base64,
            audioUrl=None,
            language=language,
            provider=self.name,
            format="wav",
            fallbackUsed=False,
        )

    async def _get_pipeline_config(self, task: SpeechTask, language: str) -> BhashiniSpeechPipelineConfig:
        key = _cache_key(task, language)
        cached = self._cache.get(key)
        if cached and cached.expires_at > time.time():
            return cached

        pipeline_id = (
            self.settings.bhashini_asr_pipeline_id
            if task == "asr"
            else self.settings.bhashini_tts_pipeline_id
        )
        payload = {
            "pipelineTasks": [
                {
                    "taskType": task,
                    "config": {"language": {"sourceLanguage": language}},
                }
            ],
            "pipelineRequestConfig": {"pipelineId": pipeline_id},
        }
        headers = {
            "userID": self.settings.bhashini_user_id,
            "ulcaApiKey": self.settings.bhashini_api_key,
        }
        data = await self._post_json(self.settings.bhashini_speech_config_url, payload, headers)
        config = _parse_pipeline_config(
            data,
            task,
            language,
            self.settings.bhashini_speech_cache_ttl_seconds,
        )
        self._cache[key] = config
        return config

    async def _post_json(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.settings.bhashini_speech_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.bhashini_speech_timeout_seconds) as client:
                    response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 429:
                    raise SpeechProviderError("Speech provider rate limit reached.")
                if response.status_code >= 500:
                    raise SpeechProviderError("Speech provider is temporarily unavailable.")
                if response.status_code >= 400:
                    raise UnsupportedSpeechLanguageError("Speech language is not supported.")
                data = response.json()
                if not isinstance(data, dict):
                    raise SpeechProviderError("Speech provider returned malformed data.")
                return data
            except (httpx.TimeoutException, httpx.TransportError, ValueError, SpeechProviderError) as error:
                last_error = error
                if attempt >= self.settings.bhashini_speech_max_retries:
                    break
        raise SpeechProviderError("Speech provider request failed.") from last_error


def _cache_key(task: SpeechTask, language: str) -> str:
    return f"{task}:{language}"


def _parse_pipeline_config(
    data: dict[str, Any],
    task: SpeechTask,
    language: str,
    ttl_seconds: int,
) -> BhashiniSpeechPipelineConfig:
    try:
        pipeline = data["pipelineResponseConfig"][0]
        service = pipeline["config"][0]
        service_id = service["serviceId"]
        callback_url = data["pipelineInferenceAPIEndPoint"]["callbackUrl"]
        auth = data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]
        header_name = auth["name"]
        header_value = auth["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise SpeechProviderError("BHASHINI speech pipeline configuration was malformed.") from error

    language_config = service.get("language", {})
    if language_config and language_config.get("sourceLanguage") not in {language, None}:
        raise UnsupportedSpeechLanguageError("BHASHINI returned a different speech language.")
    service_task = service.get("taskType") or pipeline.get("taskType")
    if service_task and service_task != task:
        raise SpeechProviderError("BHASHINI returned a different speech task.")

    return BhashiniSpeechPipelineConfig(
        service_id=service_id,
        callback_url=callback_url,
        auth_header_name=header_name,
        auth_header_value=header_value,
        expires_at=time.time() + ttl_seconds,
    )


def _extract_transcript(data: dict[str, Any]) -> str | None:
    candidates = [
        ("pipelineResponse", 0, "output", 0, "source"),
        ("pipelineResponse", 0, "output", 0, "text"),
        ("pipelineResponse", 0, "output", 0, "transcript"),
        ("output", 0, "source"),
        ("output", 0, "text"),
        ("transcript",),
    ]
    return _extract_string(data, candidates)


def _extract_audio_base64(data: dict[str, Any]) -> str | None:
    candidates = [
        ("pipelineResponse", 0, "audio", 0, "audioContent"),
        ("pipelineResponse", 0, "output", 0, "audioContent"),
        ("audio", 0, "audioContent"),
        ("audioContent",),
    ]
    return _extract_string(data, candidates)


def _extract_string(data: dict[str, Any], paths: list[tuple[Any, ...]]) -> str | None:
    for path in paths:
        value: Any = data
        try:
            for part in path:
                value = value[part]
            if isinstance(value, str) and value.strip():
                return value.strip()
        except (KeyError, IndexError, TypeError):
            continue
    return None


def _audio_format_from_mime(mime_type: str) -> str:
    if "wav" in mime_type:
        return "wav"
    if "mpeg" in mime_type or "mp3" in mime_type:
        return "mp3"
    if "mp4" in mime_type:
        return "mp4"
    if "ogg" in mime_type:
        return "ogg"
    return "webm"
