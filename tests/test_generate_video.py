"""Integration tests for the generate_video tool.

Requires GEMINI_API_KEY environment variable to be set.
Video generation is async and can take 1-5 minutes per call.
"""
from __future__ import annotations

import base64
from pathlib import Path

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


@pytest.mark.asyncio
async def test_video_with_output_dir_returns_file_path(mock_ctx_with_output_dir):
    """When MEDIA_OUTPUT_DIR is set, generate_video saves to disk and returns only the file path."""
    result = await generate_video(
        prompt="A calm ocean wave rolling onto a sandy beach, sunny day",
        model="veo-3.1",
        aspect_ratio="16:9",
        ctx=mock_ctx_with_output_dir,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    # Should return only TextContent, no EmbeddedResource
    resource_parts = [c for c in result.content if isinstance(c, EmbeddedResource)]
    assert len(resource_parts) == 0, "Expected no EmbeddedResource when output_dir is set"

    text_parts = [c for c in result.content if isinstance(c, TextContent)]
    assert len(text_parts) == 1

    path_text = text_parts[0].text
    assert "saved to:" in path_text

    file_path = path_text.split("saved to: ")[1].strip()
    saved = Path(file_path)
    assert saved.exists(), f"File not found: {file_path}"
    assert saved.suffix == ".mp4"
    assert saved.stat().st_size > 1000, "Saved video is suspiciously small"
