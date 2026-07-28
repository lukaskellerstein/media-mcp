from __future__ import annotations

import base64
import binascii
import mimetypes
from datetime import datetime, timezone
from pathlib import Path


def save_media_file(data: bytes, output_dir: str, filename: str) -> str:
    """Save media data to the output directory. Returns the absolute path."""
    path = Path(output_dir) / filename
    path.write_bytes(data)
    return str(path.resolve())


def encode_base64(data: bytes) -> str:
    """Encode bytes to base64 string for MCP responses."""
    return base64.b64encode(data).decode("utf-8")


def decode_base64(data: str) -> bytes:
    """Decode a base64 string to bytes, tolerating data-URI prefixes,
    surrounding whitespace, and missing padding."""
    if "," in data and data.lstrip().startswith("data:"):
        data = data.split(",", 1)[1]
    data = "".join(data.split())  # drop whitespace/newlines
    data += "=" * (-len(data) % 4)  # restore padding
    # validate=True so non-base64 input (e.g. a mistyped file path) raises
    # instead of being silently stripped down to garbage bytes.
    return base64.b64decode(data, validate=True)


# Magic-byte signatures → MIME type, used as a fallback when an extension
# is unavailable (e.g. raw base64 input).
_IMAGE_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # WEBP (RIFF....WEBP); good enough for routing
    (b"BM", "image/bmp"),
)


def _sniff_image_mime(data: bytes) -> str:
    for sig, mime in _IMAGE_SIGNATURES:
        if data.startswith(sig):
            return mime
    return "image/png"


# Normalized extension per MIME (avoids mimetypes quirks like ".jpe").
_MIME_EXTENSION = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
}


def extension_for_mime(mime: str | None, default: str = "png") -> str:
    """Return a bare file extension (no dot) for an image MIME type."""
    if not mime:
        return default
    mime = mime.split(";", 1)[0].strip().lower()
    if mime in _MIME_EXTENSION:
        return _MIME_EXTENSION[mime]
    guessed = mimetypes.guess_extension(mime)
    return guessed.lstrip(".") if guessed else default


def load_image_bytes(ref: str) -> tuple[bytes, str]:
    """Resolve a reference image into (bytes, mime_type).

    Accepts, in order of precedence:
      1. a ``data:<mime>;base64,...`` data URI,
      2. a path to an existing file on disk (``~`` is expanded),
      3. a raw base64 string.

    Raises ValueError with an actionable message if none of these work.
    """
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("reference image must be a non-empty string")

    # 1. data URI
    stripped = ref.lstrip()
    if stripped.startswith("data:"):
        header, _, _ = stripped.partition(",")
        mime = header[len("data:"):].split(";", 1)[0] or "image/png"
        return decode_base64(stripped), mime

    # 2. file path — guard the stat() call. A raw base64 string longer than the
    # OS path limit makes Path.is_file() raise OSError(ENAMETOOLONG) (it only
    # swallows not-found-style errors), which would otherwise crash before the
    # raw-base64 fallback below. Any OSError here just means "not a usable path".
    candidate = Path(ref.strip()).expanduser()
    try:
        is_file = candidate.is_file()
    except OSError:
        is_file = False
    if is_file:
        data = candidate.read_bytes()
        mime = mimetypes.guess_type(candidate.name)[0] or _sniff_image_mime(data)
        return data, mime

    # 3. raw base64
    try:
        data = decode_base64(ref)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(
            f"reference image is neither an existing file path nor valid "
            f"base64/data-URI: {ref[:80]!r} ({exc})"
        ) from exc
    if not data:
        raise ValueError(f"reference image decoded to empty bytes: {ref[:80]!r}")
    return data, _sniff_image_mime(data)


def generate_filename(tool_name: str, extension: str) -> str:
    """Generate a unique filename using timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{tool_name}_{ts}.{extension}"
