import pytest

from app.services.llm_client import _chat_completions_url, _parse_json_object


def test_chat_completions_url_accepts_base_root():
    assert _chat_completions_url("http://localhost:11434") == "http://localhost:11434/v1/chat/completions"


def test_chat_completions_url_accepts_v1_base():
    assert _chat_completions_url("http://localhost:11434/v1") == "http://localhost:11434/v1/chat/completions"


def test_parse_json_object_strips_markdown_fence():
    parsed = _parse_json_object('```json\n{"category":"SANITATION"}\n```')

    assert parsed["category"] == "SANITATION"


def test_parse_json_object_rejects_non_json():
    with pytest.raises(Exception):
        _parse_json_object("not json")
