import io
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.schemas.complaint import ComplaintCreate
from app.services.complaint_service import create_complaint, get_complaint_by_reference
from tests.conftest import requires_database


client = TestClient(app)


def image_bytes(image_format: str) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (16, 12), color=(20, 120, 90)).save(stream, format=image_format)
    return stream.getvalue()


@pytest.fixture(autouse=True)
def cloudinary_settings(monkeypatch):
    settings = SimpleNamespace(
        allowed_image_mime_types={"image/jpeg", "image/png", "image/webp"},
        max_upload_size_bytes=8 * 1024 * 1024,
        max_upload_size_mb=8,
        cloudinary_cloud_name="demo",
        cloudinary_api_key="key",
        cloudinary_api_secret="secret",
        cloudinary_upload_folder="mana-hyderabad/complaints",
    )
    monkeypatch.setattr("app.services.file_upload_service.get_settings", lambda: settings)


@pytest.fixture()
def mock_upload(monkeypatch):
    def upload(_file, **_kwargs):
        return {
            "secure_url": "https://res.cloudinary.com/demo/image/upload/mana-hyderabad/complaints/test.jpg",
            "public_id": "mana-hyderabad/complaints/test",
            "width": 16,
            "height": 12,
            "format": "jpg",
            "bytes": 128,
        }

    monkeypatch.setattr("cloudinary.uploader.upload", upload)


@pytest.mark.parametrize(
    ("filename", "mime_type", "image_format"),
    [
        ("sample-garbage.jpg", "image/jpeg", "JPEG"),
        ("sample-pothole.png", "image/png", "PNG"),
        ("sample-water.webp", "image/webp", "WEBP"),
    ],
)
def test_image_upload_success(filename, mime_type, image_format, mock_upload):
    response = client.post(
        "/api/uploads/images",
        files={"file": (filename, image_bytes(image_format), mime_type)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["photoUrl"].startswith("https://res.cloudinary.com/")
    assert body["publicId"] == "mana-hyderabad/complaints/test"


def test_unsupported_file_type_rejected(mock_upload):
    response = client.post(
        "/api/uploads/images",
        files={"file": ("invalid-file.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]


def test_oversized_file_rejected(monkeypatch, mock_upload):
    settings = SimpleNamespace(
        allowed_image_mime_types={"image/png"},
        max_upload_size_bytes=10,
        max_upload_size_mb=1,
        cloudinary_cloud_name="demo",
        cloudinary_api_key="key",
        cloudinary_api_secret="secret",
        cloudinary_upload_folder="mana-hyderabad/complaints",
    )
    monkeypatch.setattr("app.services.file_upload_service.get_settings", lambda: settings)
    response = client.post(
        "/api/uploads/images",
        files={"file": ("sample-pothole.png", image_bytes("PNG"), "image/png")},
    )
    assert response.status_code == 400
    assert "smaller" in response.json()["detail"]


def test_empty_file_rejected(mock_upload):
    response = client.post(
        "/api/uploads/images",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_malformed_image_rejected(mock_upload):
    response = client.post(
        "/api/uploads/images",
        files={"file": ("bad.jpg", b"not an image", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "Malformed image" in response.json()["detail"]


def test_cloudinary_failure_handled_safely(monkeypatch):
    def fail_upload(_file, **_kwargs):
        raise RuntimeError("secret failure")

    monkeypatch.setattr("cloudinary.uploader.upload", fail_upload)
    response = client.post(
        "/api/uploads/images",
        files={"file": ("sample-garbage.jpg", image_bytes("JPEG"), "image/jpeg")},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Could not upload image. Please try again."


def test_delete_temporary_image(monkeypatch):
    monkeypatch.setattr("cloudinary.uploader.destroy", lambda *_args, **_kwargs: {"result": "ok"})
    response = client.request("DELETE", "/api/uploads/images", json={"publicId": "mana-hyderabad/complaints/test"})
    assert response.status_code == 200
    assert response.json()["deleted"] is True


@requires_database
def test_complaint_submission_stores_and_returns_photo_url(db_session):
    payload = ComplaintCreate(
        originalText="Garbage is blocking the drain near Madhapur Metro.",
        normalizedEnglishText="Garbage is blocking the drain near Madhapur Metro.",
        originalLanguage="en",
        detectedLanguage="en",
        category="SANITATION",
        subcategory="GARBAGE_BLOCKING_DRAIN",
        department="MULTI_DEPARTMENT",
        priority="HIGH",
        latitude=17.4483,
        longitude=78.3915,
        landmark="Near Madhapur Metro",
        locality="Madhapur",
        photoUrl="https://res.cloudinary.com/demo/image/upload/test.jpg",
    )
    complaint = create_complaint(db_session, payload)
    tracked = get_complaint_by_reference(db_session, complaint.reference_id)
    assert tracked.photo_url == "https://res.cloudinary.com/demo/image/upload/test.jpg"


@requires_database
def test_complaint_submission_without_photo_still_works(db_session):
    complaint = create_complaint(
        db_session,
        ComplaintCreate(
            originalText="Pothole near Hitech City.",
            category="ROADS",
            priority="HIGH",
            latitude=17.4505,
            longitude=78.3804,
        ),
    )
    assert complaint.photo_url is None
