# Data Model: Media MCP Server

**Date**: 2026-03-13
**Feature**: 001-media-mcp-server

## Overview

The media-MCP server is stateless — it holds no persistent data. All
entities below are transient request/response structures that exist
only during tool invocation. The Gemini API client and server
configuration are initialized at startup via the lifespan pattern and
shared across all tool calls.

## Entities

### ServerConfig

Runtime configuration provided at server startup.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gemini_api_key` | string | yes | API key for Gemini API auth |
| `output_dir` | string | no | Directory for saving generated media files |

**Validation rules**:
- `gemini_api_key` MUST be non-empty
- `output_dir`, if provided, MUST be a writable directory path

### ImageGenerationParams

Parameters for the image generation tool.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | string | yes | — | Text description of image |
| `model` | enum | no | `nano-banana-2` | Model variant |
| `aspect_ratio` | enum | no | `1:1` | Output aspect ratio |
| `image_size` | enum | no | `1K` | Output resolution |
| `reference_images` | list[str] | no | [] | Base64-encoded reference images |
| `response_modalities` | list[str] | no | `["TEXT","IMAGE"]` | Output types |
| `thinking_level` | enum | no | `minimal` | Reasoning depth |
| `use_google_search` | bool | no | false | Enable search grounding |
| `use_image_search` | bool | no | false | Enable image search grounding |

**Enum values**:
- `model`: `nano-banana-2`, `nano-banana-pro`, `nano-banana`
- `aspect_ratio`: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`,
  `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`
- `image_size`: `512px`, `1K`, `2K`, `4K`
- `thinking_level`: `minimal`, `high`
- `response_modalities`: `TEXT`, `IMAGE`

### VideoGenerationParams

Parameters for the video generation tool.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | string | yes | — | Text description of video |
| `model` | enum | no | `veo-3.1` | Model variant |
| `aspect_ratio` | enum | no | `16:9` | Output aspect ratio |
| `resolution` | enum | no | — | Output resolution |
| `first_frame_image` | string | no | — | Base64-encoded first frame |
| `last_frame_image` | string | no | — | Base64-encoded last frame |
| `reference_images` | list[str] | no | [] | Base64-encoded reference images (max 3) |
| `extend_video_id` | string | no | — | ID of video to extend |

**Enum values**:
- `model`: `veo-3.1`, `veo-3`
- `aspect_ratio`: `16:9`, `9:16`
- `resolution`: `720p`, `1080p`, `4K`

### MusicGenerationParams

Parameters for the music generation tool.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompts` | list[MusicPrompt] | yes | — | Weighted text prompts |
| `bpm` | int | no | — | Tempo in beats per minute |
| `temperature` | float | no | 1.0 | Randomness/creativity |
| `scale` | string | no | — | Musical scale constraint |
| `duration_seconds` | int | no | — | Desired clip duration |

### MusicPrompt

A single weighted text prompt for music generation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | Description of music style/genre/instrument |
| `weight` | float | yes | Emphasis weight (higher = more influence) |

### SpeechGenerationParams

Parameters for the speech generation tool.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | yes | — | Text to convert to speech |
| `model` | enum | no | `flash-tts` | Model variant |
| `voice_name` | string | no | — | Prebuilt voice name |
| `multi_speaker` | bool | no | false | Enable multi-speaker mode |
| `speakers` | list[SpeakerMapping] | no | [] | Speaker-to-voice mappings |
| `style_instructions` | string | no | — | Natural language style guidance |

**Enum values**:
- `model`: `flash-tts`, `pro-tts`
- `voice_name`: `Kore`, `Puck`, `Charon`, `Fenrir`, `Aoede`, `Leda`,
  `Orus`, `Zephyr` (and others from Gemini)

### SpeakerMapping

Maps a speaker name to a voice for multi-speaker TTS.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Speaker identifier in the text |
| `voice_name` | string | yes | Prebuilt voice to use |

### GenerationResult

Common structure returned by all tools (conceptual — actual MCP
responses use the SDK's content types).

| Field | Type | Description |
|-------|------|-------------|
| `media_data` | bytes | Generated media as binary data |
| `media_type` | string | MIME type (image/png, audio/wav, video/mp4) |
| `file_path` | string | Optional path if saved to output directory |
| `metadata` | dict | Model used, parameters applied |

## Relationships

```text
ServerConfig ──creates──> genai.Client (at startup, via lifespan)

genai.Client ──used by──> ImageGenerationTool
genai.Client ──used by──> VideoGenerationTool
genai.Client ──used by──> SpeechGenerationTool
genai.Client ──used by──> MusicGenerationTool

MusicGenerationParams ──contains──> MusicPrompt[]
SpeechGenerationParams ──contains──> SpeakerMapping[]
```

## State Transitions

No persistent state. Each tool call is independent:

```text
Request received → Validate inputs → Call Gemini API → Return result
                                                     → Save file (if output_dir configured)
```

For async operations (video):

```text
Request received → Validate → Submit to Gemini → Poll operation
    → Done? → Download result → Return
    → Timeout? → Return timeout error
```

For streaming operations (music):

```text
Request received → Validate → Open WebSocket session
    → Accumulate audio chunks → Session ends → Return WAV
    → Error? → Cleanup session → Return error
```
