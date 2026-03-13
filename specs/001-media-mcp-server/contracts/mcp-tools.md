# MCP Tool Contracts: Media MCP Server

**Date**: 2026-03-13
**Feature**: 001-media-mcp-server
**Protocol**: Model Context Protocol (MCP)

## Overview

The media-MCP server exposes four tools via the MCP protocol. Each
tool is registered with the MCP server and discoverable by agents
through standard MCP tool listing. Tools accept structured parameters
and return media content using MCP content types.

## Tool: `generate_image`

**Description**: Generate or edit images using Google's Gemini image
generation models.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Text description of the image to generate"
    },
    "model": {
      "type": "string",
      "enum": ["nano-banana-2", "nano-banana-pro", "nano-banana"],
      "default": "nano-banana-2",
      "description": "Model variant to use"
    },
    "aspect_ratio": {
      "type": "string",
      "enum": ["1:1","1:4","1:8","2:3","3:2","3:4","4:1","4:3",
               "4:5","5:4","8:1","9:16","16:9","21:9"],
      "default": "1:1",
      "description": "Output aspect ratio"
    },
    "image_size": {
      "type": "string",
      "enum": ["512px", "1K", "2K", "4K"],
      "default": "1K",
      "description": "Output image resolution"
    },
    "reference_images": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Base64-encoded reference images"
    },
    "response_modalities": {
      "type": "array",
      "items": {"type": "string", "enum": ["TEXT", "IMAGE"]},
      "default": ["TEXT", "IMAGE"],
      "description": "Desired output types"
    },
    "thinking_level": {
      "type": "string",
      "enum": ["minimal", "high"],
      "default": "minimal",
      "description": "Reasoning depth for generation"
    },
    "use_google_search": {
      "type": "boolean",
      "default": false,
      "description": "Enable Google Search grounding"
    },
    "use_image_search": {
      "type": "boolean",
      "default": false,
      "description": "Enable Google Image Search grounding"
    }
  },
  "required": ["prompt"]
}
```

**Output**: MCP Image content (base64 PNG) + optional Text content.
If `output_dir` configured, also returns file path.

**Errors**:
- Invalid parameters → validation error with field details
- Auth failure → authentication error with guidance
- Safety filter → blocked error with filter category
- Rate limit → rate limit error with retry guidance

---

## Tool: `generate_speech`

**Description**: Generate speech audio from text using Gemini TTS
models.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Text to convert to speech"
    },
    "model": {
      "type": "string",
      "enum": ["flash-tts", "pro-tts"],
      "default": "flash-tts",
      "description": "TTS model variant"
    },
    "voice_name": {
      "type": "string",
      "description": "Prebuilt voice name (e.g., Kore, Puck)"
    },
    "multi_speaker": {
      "type": "boolean",
      "default": false,
      "description": "Enable multi-speaker mode"
    },
    "speakers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "voice_name": {"type": "string"}
        },
        "required": ["name", "voice_name"]
      },
      "description": "Speaker-to-voice mappings for multi-speaker"
    },
    "style_instructions": {
      "type": "string",
      "description": "Natural language style guidance"
    }
  },
  "required": ["text"]
}
```

**Output**: Audio data (WAV, 24kHz 16-bit mono) returned as base64
encoded audio content. If `output_dir` configured, also returns file
path.

**Errors**:
- Empty text → validation error
- Invalid voice name → validation error with available voices
- Text too long → size limit error

---

## Tool: `generate_video`

**Description**: Generate videos from text prompts or reference images
using Google's Veo models.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Text description of the video"
    },
    "model": {
      "type": "string",
      "enum": ["veo-3.1", "veo-3"],
      "default": "veo-3.1",
      "description": "Video generation model"
    },
    "aspect_ratio": {
      "type": "string",
      "enum": ["16:9", "9:16"],
      "default": "16:9",
      "description": "Output aspect ratio"
    },
    "resolution": {
      "type": "string",
      "enum": ["720p", "1080p", "4K"],
      "description": "Output resolution"
    },
    "first_frame_image": {
      "type": "string",
      "description": "Base64-encoded image for first frame"
    },
    "last_frame_image": {
      "type": "string",
      "description": "Base64-encoded image for last frame"
    },
    "reference_images": {
      "type": "array",
      "items": {"type": "string"},
      "maxItems": 3,
      "description": "Base64-encoded reference images"
    },
    "extend_video_id": {
      "type": "string",
      "description": "ID of previously generated video to extend"
    }
  },
  "required": ["prompt"]
}
```

**Output**: Video file (MP4). MCP has no native video content type,
so the video is saved to `output_dir` and the file path is returned
as text. If no `output_dir`, returns base64-encoded data via embedded
resource. Generation is async — the tool blocks until the operation
completes.

**Errors**:
- Timeout (> 5 min) → timeout error
- Invalid video ID for extension → not found error
- Safety filter → blocked error with filter category

---

## Tool: `generate_music`

**Description**: Generate instrumental music from weighted text
prompts using Google's Lyria model.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "prompts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "text": {"type": "string"},
          "weight": {"type": "number"}
        },
        "required": ["text", "weight"]
      },
      "description": "Weighted text prompts describing the music"
    },
    "bpm": {
      "type": "integer",
      "description": "Tempo in beats per minute"
    },
    "temperature": {
      "type": "number",
      "default": 1.0,
      "description": "Randomness/creativity control"
    },
    "scale": {
      "type": "string",
      "description": "Musical scale constraint"
    },
    "duration_seconds": {
      "type": "integer",
      "description": "Desired duration of output clip"
    }
  },
  "required": ["prompts"]
}
```

**Output**: Audio data (WAV, 48kHz 16-bit stereo) returned as base64
encoded audio content. If `output_dir` configured, also returns file
path.

**Errors**:
- Empty prompts → validation error
- Session disconnect → connection error with cleanup confirmation
- Experimental API unavailable → service error

---

## Common Error Response Format

All tools return errors as MCP error responses with:
- `isError: true`
- Descriptive error message including:
  - Error category (auth, validation, rate_limit, safety, timeout,
    connection)
  - Actionable guidance (what to fix or when to retry)
  - Upstream error details when available
