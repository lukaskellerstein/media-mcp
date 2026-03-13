from __future__ import annotations

import base64
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
    """Decode base64 string to bytes."""
    return base64.b64decode(data)


def generate_filename(tool_name: str, extension: str) -> str:
    """Generate a unique filename using timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{tool_name}_{ts}.{extension}"
