"""Integration tests for the generate_video tool.

Requires GEMINI_API_KEY environment variable to be set.
Video generation is async and can take 1-5 minutes per call.
"""
from __future__ import annotations

import base64

import pytest

from mcp.types import EmbeddedResource, TextContent

from tests.conftest import get_tool_fn


generate_video = get_tool_fn("generate_video")


@pytest.mark.asyncio
async def test_video_returns_base64_mp4(mock_ctx):
    """Verify generate_video returns an EmbeddedResource with base64-encoded MP4 data."""
    result = await generate_video(
        prompt="A calm ocean wave rolling onto a sandy beach, sunny day",
        model="veo-3.1",
        aspect_ratio="16:9",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    resource_parts = [c for c in result.content if isinstance(c, EmbeddedResource)]
    assert len(resource_parts) == 1, (
        f"Expected one EmbeddedResource, got content types: "
        f"{[type(c).__name__ for c in result.content]}"
    )

    resource = resource_parts[0]
    assert resource.resource.mimeType == "video/mp4"

    video_b64 = resource.resource.text
    video_bytes = base64.b64decode(video_b64)
    assert len(video_bytes) > 1000, f"Video suspiciously small: {len(video_bytes)} bytes"


@pytest.mark.asyncio
async def test_video_api_error_returns_error_result(mock_ctx):
    """Verify that a Gemini API error is surfaced as isError=True."""
    from media_mcp.tools.video import MODEL_MAP
    original = MODEL_MAP["veo-3.1"]
    MODEL_MAP["veo-3.1"] = "nonexistent-model-999"

    try:
        result = await generate_video(
            prompt="test",
            model="veo-3.1",
            ctx=mock_ctx,
        )
        assert result.isError is True, "Expected isError=True for invalid model"
        assert isinstance(result.content[0], TextContent)
    finally:
        MODEL_MAP["veo-3.1"] = original
