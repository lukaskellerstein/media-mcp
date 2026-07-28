from __future__ import annotations

import base64

import pytest

from media_mcp.utils.media import load_image_bytes

# A minimal valid PNG (1x1 transparent pixel).
_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000154a24f5f0000000049454e44ae42"
    "6082"
)


def test_load_image_bytes_from_file(tmp_path):
    p = tmp_path / "pixel.png"
    p.write_bytes(_PNG)
    data, mime = load_image_bytes(str(p))
    assert data == _PNG
    assert mime == "image/png"


def test_load_image_bytes_from_data_uri():
    uri = "data:image/png;base64," + base64.b64encode(_PNG).decode()
    data, mime = load_image_bytes(uri)
    assert data == _PNG
    assert mime == "image/png"


def test_load_image_bytes_from_raw_base64():
    raw = base64.b64encode(_PNG).decode()
    data, mime = load_image_bytes(raw)
    assert data == _PNG
    assert mime == "image/png"


def test_load_image_bytes_long_raw_base64_does_not_raise_enametoolong():
    """Regression: a raw base64 string longer than the OS path limit must fall
    through to base64 decoding instead of crashing in Path.is_file()."""
    big = base64.b64encode(_PNG * 5000).decode()  # well past PATH_MAX
    data, _ = load_image_bytes(big)
    assert data == _PNG * 5000


def test_load_image_bytes_rejects_garbage():
    with pytest.raises(ValueError):
        load_image_bytes("/no/such/file/and/not/base64/@@@")
