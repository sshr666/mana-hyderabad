import pytest

from app.services.providers.bhashini_speech_provider import (
    BhashiniSpeechProvider,
    _extract_audio_base64,
    _extract_transcript,
)


def test_extract_transcript_from_pipeline_response():
    data = {"pipelineResponse": [{"output": [{"source": "چارمینار کے پاس سڑک پر گڑھا ہے"}]}]}

    assert _extract_transcript(data) == "چارمینار کے پاس سڑک پر گڑھا ہے"


def test_extract_audio_base64_from_pipeline_response():
    data = {"pipelineResponse": [{"audio": [{"audioContent": "UklGRg=="}]}]}

    assert _extract_audio_base64(data) == "UklGRg=="


@pytest.mark.anyio
async def test_bhashini_provider_health_check_without_credentials(monkeypatch):
    provider = BhashiniSpeechProvider()
    monkeypatch.setattr(provider.settings, "bhashini_user_id", "")

    assert await provider.health_check() is False
