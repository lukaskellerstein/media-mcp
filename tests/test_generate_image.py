"""Integration tests for the generate_image tool.

Requires GEMINI_API_KEY environment variable to be set.
"""
from __future__ import annotations

import base64
from pathlib import Path

import pytest

from mcp.types import ImageContent, TextContent

from tests.conftest import get_tool_fn


generate_image = get_tool_fn("generate_image")


@pytest.mark.asyncio
async def test_image_returns_image_content(mock_ctx):
    """Verify generate_image returns at least one ImageContent with valid base64 PNG data."""
    result = await generate_image(
        prompt="A solid red square on a white background",
        model="nano-banana-2",
        aspect_ratio="1:1",
        image_size="512px",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    image_parts = [c for c in result.content if isinstance(c, ImageContent)]
    assert len(image_parts) >= 1, (
        f"Expected at least one ImageContent, got content types: "
        f"{[type(c).__name__ for c in result.content]}"
    )

    img = image_parts[0]
    assert img.mimeType == "image/png", f"Expected image/png, got {img.mimeType}"

    decoded = base64.b64decode(img.data)
    assert decoded[:8] == b"\x89PNG\r\n\x1a\n", "Data is not valid PNG"
    assert len(decoded) > 100, f"Image suspiciously small: {len(decoded)} bytes"


@pytest.mark.asyncio
async def test_image_with_text_and_image_response(mock_ctx):
    """Verify generate_image does not error when TEXT+IMAGE modalities are requested.

    The API may not always return both modalities, so we only assert no error.
    """
    result = await generate_image(
        prompt="Draw a simple circle and describe what you drew",
        model="nano-banana-2",
        response_modalities=["TEXT", "IMAGE"],
        image_size="512px",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"


@pytest.mark.asyncio
async def test_image_api_error_returns_error_result(mock_ctx):
    """Verify that a Gemini API error is surfaced as isError=True with a categorized message."""
    from media_mcp.tools.image import MODEL_MAP
    original = MODEL_MAP["nano-banana-2"]
    MODEL_MAP["nano-banana-2"] = "nonexistent-model-999"

    try:
        result = await generate_image(
            prompt="test",
            model="nano-banana-2",
            image_size="512px",
            ctx=mock_ctx,
        )
        assert result.isError is True, "Expected isError=True for invalid model"
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)
    finally:
        MODEL_MAP["nano-banana-2"] = original


@pytest.mark.asyncio
async def test_image_with_output_dir_returns_file_path(mock_ctx_with_output_dir):
    """When MEDIA_OUTPUT_DIR is set, generate_image saves to disk and returns only the file path."""
    result = await generate_image(
        prompt="A solid blue square on a white background",
        model="nano-banana-2",
        aspect_ratio="1:1",
        image_size="512px",
        ctx=mock_ctx_with_output_dir,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    # Should return only TextContent, no ImageContent
    image_parts = [c for c in result.content if isinstance(c, ImageContent)]
    assert len(image_parts) == 0, "Expected no ImageContent when output_dir is set"

    text_parts = [c for c in result.content if isinstance(c, TextContent)]
    assert len(text_parts) >= 1

    path_text = text_parts[0].text
    assert "saved to:" in path_text

    # Verify the file actually exists and is valid PNG
    file_path = path_text.split("saved to: ")[1].strip()
    saved = Path(file_path)
    assert saved.exists(), f"File not found: {file_path}"
    assert saved.stat().st_size > 100, "Saved file is suspiciously small"
    assert saved.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "Saved file is not valid PNG"
