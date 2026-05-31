import pytest

from app.services.providers.bhashini_provider import BhashiniTranslationProvider
from app.services.providers.base_translation_provider import TranslationProviderError


@pytest.mark.anyio
async def test_bhashini_provider_fails_safely_when_unconfigured(monkeypatch):
    provider = BhashiniTranslationProvider()
    monkeypatch.setattr(provider, "settings", provider.settings.model_copy(update={"bhashini_api_key": ""}))

    with pytest.raises(TranslationProviderError):
        await provider.translate("నమస్తే", "te", "en")
