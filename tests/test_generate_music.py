"""Integration tests for the generate_music tool.

Requires GEMINI_API_KEY environment variable to be set.
Music generation uses WebSocket streaming and can take 30+ seconds.
"""
from __future__ import annotations

import base64
import io
import wave

import pytest

from mcp.types import AudioContent, TextContent

from tests.conftest import get_tool_fn


generate_music = get_tool_fn("generate_music")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Lyria RealTime is experimental — endpoint returns 404 for most API keys")
async def test_music_returns_audio_content(mock_ctx):
    """Verify generate_music returns AudioContent with valid base64 WAV data."""
    result = await generate_music(
        prompts=[{"text": "calm piano", "weight": 1.0}],
        duration_seconds=5,
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 1, (
        f"Expected one AudioContent, got: "
        f"{[type(c).__name__ for c in result.content]}"
    )

    audio = audio_parts[0]
    assert audio.mimeType == "audio/wav", f"Expected audio/wav, got {audio.mimeType}"

    decoded = base64.b64decode(audio.data)
    assert decoded[:4] == b"RIFF", "Data does not start with RIFF header"
    assert decoded[8:12] == b"WAVE", "Data is not WAVE format"

    wav_io = io.BytesIO(decoded)
    with wave.open(wav_io, "rb") as wf:
        assert wf.getnchannels() == 2, f"Expected stereo, got {wf.getnchannels()} channels"
        assert wf.getsampwidth() == 2, f"Expected 16-bit, got {wf.getsampwidth() * 8}-bit"
        assert wf.getframerate() == 48000, f"Expected 48kHz, got {wf.getframerate()}Hz"
        assert wf.getnframes() > 0, "WAV has zero frames"


@pytest.mark.asyncio
async def test_music_empty_prompts_returns_validation_error(mock_ctx):
    """Verify empty prompts list returns a validation error."""
    result = await generate_music(
        prompts=[],
        ctx=mock_ctx,
    )

    assert result.isError is True
    assert isinstance(result.content[0], TextContent)
    assert "[validation]" in result.content[0].text


@pytest.mark.asyncio
@pytest.mark.skip(reason="Lyria RealTime is experimental — endpoint returns 404 for most API keys")
async def test_music_with_bpm_and_scale(mock_ctx):
    """Verify music generation works with BPM and scale constraints."""
    result = await generate_music(
        prompts=[{"text": "upbeat electronic", "weight": 1.0}],
        bpm=120,
        scale="C_MAJOR_A_MINOR",
        duration_seconds=5,
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"
    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 1
