from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_detect_language_endpoint():
    response = client.post(
        "/api/translation/detect-language",
        json={"text": "Madhapur metro దగ్గర garbage dump అయింది"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["detectedLanguage"] == "te-en"
    assert body["isMixedLanguage"] is True


def test_translate_endpoint_rejects_empty_text():
    response = client.post(
        "/api/translation/translate",
        json={"text": "   ", "targetLanguage": "en"},
    )

    assert response.status_code == 422


def test_translate_endpoint_returns_fallback_without_credentials():
    response = client.post(
        "/api/translation/translate",
        json={
            "text": "Road pe bahut waterlogging hai near Gachibowli signal",
            "sourceLanguage": "hi",
            "targetLanguage": "en",
            "preserveTerms": ["Gachibowli signal"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] in {"FALLBACK", "BHASHINI", "INDIC_TRANS2"}
    assert "Gachibowli signal" in body["translatedText"]
