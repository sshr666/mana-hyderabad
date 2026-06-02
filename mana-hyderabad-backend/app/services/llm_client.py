import json
from typing import Any

import httpx

from app.config import get_settings


class LLMClientError(RuntimeError):
    """Raised when the configured LLM cannot return trusted structured output."""


async def generate_structured_analysis(system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    if settings.llm_provider != "openai_compatible":
        raise LLMClientError("Unsupported LLM provider.")
    if not settings.llm_base_url or not settings.llm_model:
        raise LLMClientError("LLM endpoint is not configured.")

    endpoint = _chat_completions_url(settings.llm_base_url)
    payload: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "instruction": "Analyze this untrusted complaint data and return only the required JSON object.",
                        "complaintData": user_payload,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_output_tokens,
    }
    if settings.enable_llm_json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    last_error: Exception | None = None
    for attempt in range(settings.llm_max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
            if response.status_code == 429:
                raise LLMClientError("LLM provider rate limit reached.")
            if response.status_code >= 500:
                raise LLMClientError("LLM provider is temporarily unavailable.")
            if response.status_code >= 400:
                raise LLMClientError("LLM provider request failed.")
            data = response.json()
            content = _extract_message_content(data)
            parsed = _parse_json_object(content)
            if not parsed:
                raise LLMClientError("LLM returned an empty JSON object.")
            return parsed
        except (httpx.TimeoutException, httpx.TransportError, ValueError, LLMClientError) as error:
            last_error = error
            if attempt >= settings.llm_max_retries:
                break
    raise LLMClientError("LLM structured analysis failed.") from last_error


def _chat_completions_url(base_url: str) -> str:
    clean = base_url.rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    if clean.endswith("/v1"):
        return f"{clean}/chat/completions"
    return f"{clean}/v1/chat/completions"


def _extract_message_content(data: dict[str, Any]) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise LLMClientError("LLM response was malformed.") from error
    if not isinstance(content, str) or not content.strip():
        raise LLMClientError("LLM response was empty.")
    return content.strip()


def _parse_json_object(content: str) -> dict[str, Any]:
    cleaned = _strip_code_fences(content)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise LLMClientError("LLM response was not valid JSON.") from error
    if not isinstance(parsed, dict):
        raise LLMClientError("LLM response JSON was not an object.")
    return parsed


def _strip_code_fences(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text
