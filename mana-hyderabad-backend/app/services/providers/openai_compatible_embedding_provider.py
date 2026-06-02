import asyncio
from typing import Any

import httpx

from app.config import get_settings
from app.services.providers.base_embedding_provider import BaseEmbeddingProvider


class EmbeddingProviderError(RuntimeError):
    pass


class OpenAICompatibleEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_embedding(self, text: str) -> list[float]:
        if not self.settings.embedding_api_key or not self.settings.embedding_base_url or not self.settings.embedding_model:
            raise EmbeddingProviderError("Embedding provider is not configured.")
        payload = {"model": self.settings.embedding_model, "input": text}
        endpoint = self.settings.embedding_base_url.rstrip("/")
        if not endpoint.endswith("/embeddings"):
            endpoint = f"{endpoint}/embeddings"
        headers = {"Authorization": f"Bearer {self.settings.embedding_api_key}"}

        last_error: Exception | None = None
        for attempt in range(self.settings.embedding_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.embedding_timeout_seconds) as client:
                    response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise EmbeddingProviderError("Embedding provider is temporarily unavailable.")
                response.raise_for_status()
                data = response.json()
                return self._parse_embedding(data)
            except (httpx.HTTPError, ValueError, EmbeddingProviderError) as exc:
                last_error = exc
                if attempt < self.settings.embedding_max_retries:
                    await asyncio.sleep(0.25 * (attempt + 1))
        raise EmbeddingProviderError("Could not generate embedding.") from last_error

    async def health_check(self) -> bool:
        return bool(self.settings.embedding_api_key and self.settings.embedding_base_url and self.settings.embedding_model)

    def _parse_embedding(self, data: dict[str, Any]) -> list[float]:
        try:
            embedding = data["data"][0]["embedding"]
        except (KeyError, IndexError, TypeError) as exc:
            raise EmbeddingProviderError("Malformed embedding response.") from exc
        if not isinstance(embedding, list) or not embedding:
            raise EmbeddingProviderError("Embedding response did not include a vector.")
        vector = [float(value) for value in embedding]
        if len(vector) != self.settings.embedding_dimensions:
            raise EmbeddingProviderError("Embedding vector dimensions did not match configuration.")
        return vector
