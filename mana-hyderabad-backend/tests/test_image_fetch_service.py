import pytest

from app.services.image_fetch_service import ImageFetchError, validate_image_bytes, validate_photo_url


def test_rejects_insecure_url():
    with pytest.raises(ImageFetchError) as error:
        validate_photo_url("http://example.com/image.jpg")
    assert error.value.code == "INSECURE_IMAGE_URL"


def test_rejects_localhost_url():
    with pytest.raises(ImageFetchError) as error:
        validate_photo_url("https://localhost/image.jpg")
    assert error.value.code == "PRIVATE_IMAGE_HOST"


def test_rejects_file_url():
    with pytest.raises(ImageFetchError) as error:
        validate_photo_url("file:///tmp/image.jpg")
    assert error.value.code == "UNSUPPORTED_PROTOCOL"


def test_corrupt_image_rejected():
    with pytest.raises(ImageFetchError) as error:
        validate_image_bytes(b"not an image")
    assert error.value.code == "MALFORMED_IMAGE"
