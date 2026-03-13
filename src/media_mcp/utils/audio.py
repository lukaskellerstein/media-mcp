from __future__ import annotations

import io
import wave


def pcm_to_wav_speech(data: bytes) -> bytes:
    """Convert raw PCM audio to WAV format for speech (24kHz, mono, 16-bit)."""
    return _pcm_to_wav(data, channels=1, sample_width=2, frame_rate=24000)


def pcm_to_wav_music(data: bytes) -> bytes:
    """Convert raw PCM audio to WAV format for music (48kHz, stereo, 16-bit)."""
    return _pcm_to_wav(data, channels=2, sample_width=2, frame_rate=48000)


def _pcm_to_wav(
    data: bytes,
    channels: int,
    sample_width: int,
    frame_rate: int,
) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(frame_rate)
        wf.writeframes(data)
    return buf.getvalue()
