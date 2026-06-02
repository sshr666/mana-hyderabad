from fastapi.testclient import TestClient

import app.api.vision as vision_api
from app.main import app
from app.models.complaint import VisionStatus
from app.schemas.vision import VisionAnalysisResponse


client = TestClient(app)


def test_vision_health_endpoint():
    response = client.get("/api/vision/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "modelConfigured" in body


def test_direct_analyse_uses_safe_response(monkeypatch):
    async def fake_analyse_photo_url(_photo_url: str):
        return VisionAnalysisResponse(
            status=VisionStatus.NOT_CONFIGURED,
            detectedObjects=[],
            citizenMessage="Image uploaded successfully. Automated image analysis is currently unavailable. Field verification may still be required.",
            adminSummary="Computer-vision model is not configured. Review the uploaded image manually.",
            modelVersion="test",
            processedAt=None,
            requiresHumanVerification=True,
            inferenceDurationMs=None,
        )

    monkeypatch.setattr(vision_api, "analyse_photo_url", fake_analyse_photo_url)
    response = client.post("/api/vision/analyse", json={"photoUrl": "https://res.cloudinary.com/demo/image.jpg"})
    assert response.status_code == 200
    assert response.json()["status"] == "NOT_CONFIGURED"
