import functools
import hashlib
import math
import re
from datetime import datetime, timezone

from app.config import get_settings
from app.schemas.duplicate import EmbeddingResult
from app.services.providers.openai_compatible_embedding_provider import (
    EmbeddingProviderError,
    OpenAICompatibleEmbeddingProvider,
)


def build_embedding_source_text(
    *,
    normalized_english_text: str,
    category: str,
    landmark: str | None,
    locality: str | None,
) -> str:
    complaint_text = normalize_whitespace(normalized_english_text)
    return "\n".join(
        [
            f"Category: {category}",
            f"Complaint: {complaint_text}",
            f"Landmark: {normalize_whitespace(landmark) if landmark else 'Not provided'}",
            f"Locality: {normalize_whitespace(locality) if locality else 'Not provided'}",
        ]
    )


async def generate_complaint_embedding(
    *,
    normalized_english_text: str,
    category: str,
    landmark: str | None,
    locality: str | None,
) -> EmbeddingResult:
    settings = get_settings()
    source_text = build_embedding_source_text(
        normalized_english_text=normalized_english_text,
        category=category,
        landmark=landmark,
        locality=locality,
    )
    if not normalize_whitespace(normalized_english_text):
        raise EmbeddingProviderError("Normalized complaint text is required for embeddings.")

    try:
        provider = OpenAICompatibleEmbeddingProvider()
        embedding = await provider.generate_embedding(source_text)
        return EmbeddingResult(
            embedding=embedding,
            sourceText=source_text,
            provider=settings.embedding_provider,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        )
    except EmbeddingProviderError:
        if not settings.enable_embedding_fallback:
            raise
        embedding = deterministic_embedding(source_text, settings.embedding_dimensions)
        return EmbeddingResult(
            embedding=embedding,
            sourceText=source_text,
            provider="DETERMINISTIC_FALLBACK",
            model="local-hash-bow",
            dimensions=settings.embedding_dimensions,
        )


def generate_complaint_embedding_sync(
    *,
    normalized_english_text: str,
    category: str,
    landmark: str | None,
    locality: str | None,
) -> EmbeddingResult:
    import anyio

    return anyio.run(
        functools.partial(
            generate_complaint_embedding,
            normalized_english_text=normalized_english_text,
            category=category,
            landmark=landmark,
            locality=locality,
        )
    )


def deterministic_embedding(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    tokens = re.findall(r"[\w]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def normalize_whitespace(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
