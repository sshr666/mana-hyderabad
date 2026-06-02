from __future__ import annotations

import ipaddress
import socket
from io import BytesIO
from urllib.parse import urlparse

import httpx
from PIL import Image, UnidentifiedImageError

from app.config import get_settings


class ImageFetchError(RuntimeError):
    def __init__(self, message: str, code: str = "IMAGE_FETCH_FAILED") -> None:
        super().__init__(message)
        self.code = code


ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def fetch_image_bytes(photo_url: str) -> bytes:
    settings = get_settings()
    parsed = validate_photo_url(photo_url)
    await reject_private_host(parsed.hostname or "")
    headers = {"Accept": "image/jpeg,image/png,image/webp"}
    try:
        async with httpx.AsyncClient(
            timeout=settings.vision_image_download_timeout_seconds,
            follow_redirects=False,
        ) as client:
            response = await client.get(photo_url, headers=headers)
    except httpx.HTTPError as exc:
        raise ImageFetchError("Could not download image.", "IMAGE_DOWNLOAD_FAILED") from exc
    if response.is_redirect:
        location = response.headers.get("location", "")
        redirected = validate_photo_url(location)
        await reject_private_host(redirected.hostname or "")
        if (redirected.hostname or "").lower() != (parsed.hostname or "").lower():
            raise ImageFetchError("Redirected image host is not trusted.", "UNTRUSTED_REDIRECT")
        try:
            async with httpx.AsyncClient(
                timeout=settings.vision_image_download_timeout_seconds,
                follow_redirects=False,
            ) as client:
                response = await client.get(location, headers=headers)
        except httpx.HTTPError as exc:
            raise ImageFetchError("Could not download redirected image.", "IMAGE_DOWNLOAD_FAILED") from exc
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ImageFetchError("Image host returned an error.", "IMAGE_DOWNLOAD_FAILED") from exc
    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ImageFetchError("Unsupported image MIME type.", "UNSUPPORTED_IMAGE_TYPE")
    content = response.content
    if not content:
        raise ImageFetchError("Image response was empty.", "EMPTY_IMAGE")
    if len(content) > settings.vision_max_image_size_bytes:
        raise ImageFetchError("Image is too large for vision analysis.", "IMAGE_TOO_LARGE")
    validate_image_bytes(content)
    return content


def validate_photo_url(photo_url: str):
    settings = get_settings()
    parsed = urlparse(photo_url)
    if parsed.scheme not in {"https", "http"}:
        raise ImageFetchError("Unsupported image URL protocol.", "UNSUPPORTED_PROTOCOL")
    if parsed.scheme != "https":
        raise ImageFetchError("Image URL must use HTTPS.", "INSECURE_IMAGE_URL")
    if not parsed.hostname:
        raise ImageFetchError("Image URL host is missing.", "MISSING_HOST")
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        raise ImageFetchError("Localhost image URLs are not allowed.", "PRIVATE_IMAGE_HOST")
    trusted_hosts = settings.trusted_vision_image_hosts
    if not trusted_hosts:
        raise ImageFetchError("Trusted image hosts are not configured.", "HOST_ALLOWLIST_NOT_CONFIGURED")
    if host not in trusted_hosts:
        raise ImageFetchError("Image host is not trusted for vision analysis.", "UNTRUSTED_IMAGE_HOST")
    return parsed


async def reject_private_host(hostname: str) -> None:
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ImageFetchError("Could not resolve image host.", "HOST_RESOLUTION_FAILED") from exc
    for address in addresses:
        ip_value = address[4][0]
        ip = ipaddress.ip_address(ip_value)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ImageFetchError("Private network image URLs are not allowed.", "PRIVATE_IMAGE_HOST")


def validate_image_bytes(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageFetchError("Image payload is malformed.", "MALFORMED_IMAGE") from exc
