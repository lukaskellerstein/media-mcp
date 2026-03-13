# Research: Media MCP Server

**Date**: 2026-03-13
**Feature**: 001-media-mcp-server

## 1. Python MCP SDK

**Decision**: Use `mcp` package (modelcontextprotocol/python-sdk) with
FastMCP high-level API.

**Rationale**: FastMCP is the official, recommended way to build MCP
servers in Python. It provides decorators for tool registration,
built-in Image type for binary responses, lifespan management for
shared resources, and stdio/SSE transport out of the box.

**Alternatives considered**:
- Raw MCP protocol implementation: rejected — unnecessary complexity,
  the SDK handles serialization, transport, and protocol negotiation.
- Node.js MCP SDK: rejected — constitution mandates Python as primary
  language.

**Key findings**:
- Install: `uv add "mcp[cli]"` (v1.26.0+, requires Python >=3.10)
- Server: `FastMCP("server-name")` with `@mcp.tool()` decorator
- Image return: `from mcp.server.fastmcp import Image` — accepts
  `data` (bytes) and `format` (str)
- Audio return: `AudioContent(type="audio", data=base64_str,
  mimeType="audio/wav")` — native MCP audio content type
- Complex responses: return `CallToolResult` with mixed content
  blocks (`TextContent`, `ImageContent`, `AudioContent`)
- Video: no native MCP video content type — return file path via
  `TextContent` or `EmbeddedResource` with base64 data
- Stdio transport: `mcp.run()` (default)
- SSE transport: `mcp.run(transport="sse")`
- Streamable HTTP: `mcp.run(transport="streamable-http")`
- Lifespan: async context manager yielding shared state (API client)
- Context: `ctx.report_progress()` for long-running operations,
  `ctx.info()/error()` for logging
- Tool parameters: derived from function type hints; supports
  Pydantic BaseModel, TypedDict, dataclasses for structured output
- Dev mode: `uv run mcp dev src/media_mcp/server.py` (MCP Inspector)
- Build system: `setuptools` (not hatchling, per constitution)

## 2. Google Gemini Python Client

**Decision**: Use `google-genai` package for all Gemini API
interactions.

**Rationale**: `google-genai` is Google's current-generation Python
SDK for the Gemini API. It provides typed wrappers for all endpoints
including image generation, video generation (Veo), TTS, and supports
the async polling pattern needed for video operations.

**Alternatives considered**:
- `google-generativeai`: older package, being superseded by
  `google-genai`
- Direct REST calls: rejected — the SDK handles auth, retries,
  polling, and type safety
- `google-cloud-aiplatform`: rejected — Vertex AI focused, not needed
  for API key auth

**Key findings**:
- Install: `uv add google-genai`
- Client: `from google import genai; client = genai.Client(api_key=key)`
- All model calls go through `client.models.*`

## 3. Image Generation (Nano Banana)

**Decision**: Use `client.models.generate_content()` with image
generation models.

**Rationale**: Image generation in Gemini uses the standard
`generate_content` endpoint with image-capable models. The response
contains inline image data as base64.

**Key findings**:
- Models: `gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`,
  `gemini-2.5-flash-image`
- Call: `client.models.generate_content(model=model, contents=prompt,
  config=config)`
- Config: `types.GenerateContentConfig(
  response_modalities=["TEXT", "IMAGE"],
  image_config=types.ImageConfig(aspect_ratio="16:9",
  image_size="2K"),
  thinking_config=types.ThinkingConfig(thinking_level="High"))`
- Response: iterate `response.parts`, check `part.inline_data` for
  images (`part.as_image()` returns PIL Image) or `part.text` for text
- Reference images: pass PIL Image objects directly in contents list
  alongside text prompt: `contents=["prompt text", pil_img1, pil_img2]`
- Aspect ratio values: 1:1, 1:4, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4,
  9:16, 16:9, 21:9
- Image size values: 512, 1K, 2K, 4K

## 4. Video Generation (Veo)

**Decision**: Use `client.models.generate_videos()` with async polling
via `client.operations.get()`.

**Rationale**: Video generation is inherently async — Veo returns an
operation that must be polled until complete.

**Key findings**:
- Models: `veo-3.1-generate-preview`, `veo-3.0-generate-preview`
- Call: `client.models.generate_videos(model=model, prompt=prompt,
  config=config)`
- Polling: `while not operation.done: time.sleep(10);
  operation = client.operations.get(operation)`
- Config: `types.GenerateVideosConfig(aspect_ratio=...,
  resolution=..., last_frame=..., reference_images=[...])`
- First frame: pass as `image=` parameter directly
- Last frame: pass via `config.last_frame`
- Reference images: `types.VideoGenerationReferenceImage(image=img,
  reference_type="asset")`
- Video extension: pass `video=` parameter from previous generation
- Result: `operation.response.generated_videos[0].video.save(path)`
  or download bytes

## 5. Speech Generation (TTS)

**Decision**: Use `client.models.generate_content()` with TTS models
and speech config.

**Rationale**: TTS in Gemini uses the standard generate_content
endpoint with speech-specific configuration.

**Key findings**:
- Models: `gemini-2.5-flash-preview-tts`,
  `gemini-2.5-pro-preview-tts`
- Call: `client.models.generate_content(model=model, contents=text,
  config=config)`
- Config: `types.GenerateContentConfig(
  response_modalities=["AUDIO"],
  speech_config=types.SpeechConfig(
    voice_config=types.VoiceConfig(
      prebuilt_voice_config=types.PrebuiltVoiceConfig(
        voice_name="Kore"))))`
- Multi-speaker config:
  `types.SpeechConfig(multi_speaker_voice_config=
  types.MultiSpeakerVoiceConfig(speaker_voice_configs=[
  types.SpeakerVoiceConfig(speaker="Joe",
  voice_config=types.VoiceConfig(
  prebuilt_voice_config=types.PrebuiltVoiceConfig(
  voice_name="Kore")))]))`
- Multi-speaker text format: `"Joe: Hello! Jane: Hi there!"`
- Style: embed natural language instructions in the text prompt
  (e.g., "Say cheerfully: Hello!") — TTS model only does TTS, no
  reasoning
- Available voices: Kore, Puck, Zephyr, Charon, Fenrir, Leda, Orus,
  Aoede, and ~24 others
- Output format: `audio/L16;codec=pcm;rate=24000` — 24kHz, mono,
  16-bit PCM
- Extract: `response.candidates[0].content.parts[0].inline_data.data`
- WAV: `wave.open()` with nchannels=1, sampwidth=2, framerate=24000

## 6. Music Generation (Lyria)

**Decision**: Use `client.aio.live.connect()` with the Lyria RealTime
model for WebSocket-based streaming.

**Rationale**: Lyria RealTime is the only music generation option in
the Gemini ecosystem. It uses a streaming WebSocket protocol that
differs from all other endpoints.

**Key findings**:
- Model: `lyria-realtime-exp`
- Connection: `async with client.aio.live.music.connect(
  model="models/lyria-realtime-exp") as session`
- Prompts: `session.set_weighted_prompts(prompts=[
  types.WeightedPrompt(text="minimal techno", weight=1.0)])`
  — weights are normalized, must not all be zero
- Config: `session.set_music_generation_config(
  config=types.LiveMusicGenerationConfig(bpm=120,
  temperature=1.1, scale=types.Scale.D_MAJOR_B_MINOR,
  guidance=4.0, density=0.5, brightness=0.5))`
- Additional params: top_k (1-1000, default 40), seed (optional),
  mute_bass, mute_drums, only_bass_and_drums,
  music_generation_mode ("QUALITY"|"DIVERSITY"|"VOCALIZATION")
- Playback: `session.play()`, `session.pause()`, `session.stop()`
- Context reset: `session.reset_context()` required after changing
  BPM or scale
- Audio chunks: `async for msg in session.receive():
  msg.server_content.audio_chunks[0].data`
- Output format: raw 16-bit PCM, **48kHz, stereo (2 channels)**
  — chunks arrive ~2 seconds apart, all SynthID watermarked
- WAV: `wave.open()` with nchannels=2, sampwidth=2, framerate=48000
- Scale enum: C_MAJOR_A_MINOR, D_FLAT_MAJOR_B_FLAT_MINOR,
  D_MAJOR_B_MINOR, E_FLAT_MAJOR_C_MINOR, E_MAJOR_D_FLAT_MINOR,
  F_MAJOR_D_MINOR, G_FLAT_MAJOR_E_FLAT_MINOR, G_MAJOR_E_MINOR,
  A_FLAT_MAJOR_F_MINOR, A_MAJOR_G_FLAT_MINOR,
  B_FLAT_MAJOR_G_MINOR, B_MAJOR_A_FLAT_MINOR
- Session lifecycle: must explicitly close/cleanup on error
- Note: experimental v1alpha API — may change

## 7. Project Structure Decision

**Decision**: Single-project flat structure under `src/media_mcp/`.

**Rationale**: This is a single-purpose MCP server with no frontend.
A flat module structure under a single package is the simplest
approach that meets requirements (Constitution Principle I: Simplicity
First).

```text
src/media_mcp/
├── __init__.py
├── server.py          # FastMCP server, tool registration, lifespan
├── config.py          # Server configuration (API key, output dir)
├── tools/
│   ├── __init__.py
│   ├── image.py       # Image generation tool
│   ├── video.py       # Video generation tool
│   ├── speech.py      # Speech generation tool
│   └── music.py       # Music generation tool
└── utils/
    ├── __init__.py
    └── audio.py        # WAV header construction, audio utilities

tests/
├── __init__.py
├── test_image.py
├── test_video.py
├── test_speech.py
├── test_music.py
└── test_config.py
```

## 8. Dependency Summary

| Package | Purpose | Version |
|---------|---------|---------|
| `mcp` | MCP server SDK (FastMCP) | latest |
| `google-genai` | Gemini API client | latest |
| `pydantic` | Input validation, config | >= 2.0 |

No additional dependencies needed. The MCP SDK handles transport.
`google-genai` handles all API interactions. Standard library `struct`
and `wave` handle WAV file creation.
