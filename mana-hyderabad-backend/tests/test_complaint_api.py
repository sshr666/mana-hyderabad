from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyse_endpoint_classifies_mixed_language_waterlogging():
    response = client.post(
        "/api/complaints/analyse",
        json={
            "text": "Road pe bahut waterlogging hai near Gachibowli signal",
            "language": "hi",
            "photoUrl": None,
            "latitude": None,
            "longitude": None,
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["category"] == "WATERLOGGING"
    assert body["locationText"] == "Gachibowli signal"
    assert body["missingFields"] == ["gps_location"]


def test_submit_validation_rejects_empty_text():
    response = client.post(
        "/api/complaints",
        json={
            "originalText": "",
            "category": "SANITATION",
            "priority": "MEDIUM",
        },
    )
    assert response.status_code == 422
