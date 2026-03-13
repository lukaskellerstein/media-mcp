"""Integration tests for the generate_speech tool.

Requires GEMINI_API_KEY environment variable to be set.
"""
from __future__ import annotations

import base64
import io
import wave
from pathlib import Path

import pytest

from mcp.types import AudioContent, TextContent

from tests.conftest import get_tool_fn


generate_speech = get_tool_fn("generate_speech")


@pytest.mark.asyncio
async def test_speech_returns_audio_content(mock_ctx):
    """Verify generate_speech returns AudioContent with valid base64 WAV data."""
    result = await generate_speech(
        text="Hello world",
        model="flash-tts",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 1, (
        f"Expected exactly one AudioContent, got: "
        f"{[type(c).__name__ for c in result.content]}"
    )

    audio = audio_parts[0]
    assert audio.mimeType == "audio/wav", f"Expected audio/wav, got {audio.mimeType}"

    decoded = base64.b64decode(audio.data)
    assert decoded[:4] == b"RIFF", "Data does not start with RIFF header"
    assert decoded[8:12] == b"WAVE", "Data is not WAVE format"

    wav_io = io.BytesIO(decoded)
    with wave.open(wav_io, "rb") as wf:
        assert wf.getnchannels() == 1, f"Expected mono, got {wf.getnchannels()} channels"
        assert wf.getsampwidth() == 2, f"Expected 16-bit, got {wf.getsampwidth() * 8}-bit"
        assert wf.getframerate() == 24000, f"Expected 24kHz, got {wf.getframerate()}Hz"
        assert wf.getnframes() > 0, "WAV has zero frames"


@pytest.mark.asyncio
async def test_speech_with_voice_name(mock_ctx):
    """Verify speech generation works with a specific voice."""
    result = await generate_speech(
        text="The quick brown fox jumps over the lazy dog near the riverbank on a warm summer afternoon.",
        model="flash-tts",
        voice_name="Kore",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"
    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 1


@pytest.mark.asyncio
async def test_speech_with_style_instructions(mock_ctx):
    """Verify speech generation works with style instructions."""
    result = await generate_speech(
        text="Good morning everyone",
        model="flash-tts",
        style_instructions="Say cheerfully and energetically",
        ctx=mock_ctx,
    )

    assert not result.isError, f"Tool returned error: {result.content}"
    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 1


@pytest.mark.asyncio
async def test_speech_empty_text_returns_validation_error(mock_ctx):
    """Verify empty text input returns a validation error."""
    result = await generate_speech(
        text="   ",
        ctx=mock_ctx,
    )

    assert result.isError is True
    assert isinstance(result.content[0], TextContent)
    assert "[validation]" in result.content[0].text


@pytest.mark.asyncio
async def test_speech_with_output_dir_returns_file_path(mock_ctx_with_output_dir):
    """When MEDIA_OUTPUT_DIR is set, generate_speech saves to disk and returns only the file path."""
    result = await generate_speech(
        text="Hello world",
        model="flash-tts",
        ctx=mock_ctx_with_output_dir,
    )

    assert not result.isError, f"Tool returned error: {result.content}"

    # Should return only TextContent, no AudioContent
    audio_parts = [c for c in result.content if isinstance(c, AudioContent)]
    assert len(audio_parts) == 0, "Expected no AudioContent when output_dir is set"

    text_parts = [c for c in result.content if isinstance(c, TextContent)]
    assert len(text_parts) == 1

    path_text = text_parts[0].text
    assert "saved to:" in path_text

    file_path = path_text.split("saved to: ")[1].strip()
    saved = Path(file_path)
    assert saved.exists(), f"File not found: {file_path}"
    assert saved.suffix == ".wav"
    assert saved.stat().st_size > 100, "Saved file is suspiciously small"

    data = saved.read_bytes()
    assert data[:4] == b"RIFF", "Saved file is not RIFF/WAV"
