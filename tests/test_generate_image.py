"""Integration tests for the generate_image tool.

Requires GEMINI_API_KEY environment variable to be set.
"""
from __future__ import annotations

import base64

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
    """Verify generate_image can return both text and image when modalities include TEXT."""
    result = await generate_image(
        prompt="Draw a simple circle and describe what you drew",
        model="nano-banana-2",
        response_modalities=["TEXT", "IMAGE"],
        image_size="512px",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"
    content_types = {type(c).__name__ for c in result.content}
    assert "ImageContent" in content_types, f"No image in response: {content_types}"


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
