# media-mcp

MCP server for AI-powered media generation using Google Gemini. Generate images, videos, music, and speech directly from your AI agent.

## Features

- **Image Generation** — Create and edit images using Gemini's Nano Banana models with support for multiple aspect ratios, resolutions up to 4K, and reference images
- **Video Generation** — Generate videos with native audio, dialogue, and sound effects using Veo models (text-to-video, image-to-video, video extension)
- **Music Generation** — Create instrumental music with weighted text prompts using Lyria RealTime (genre, instrument, mood control with BPM and scale)
- **Speech Generation** — Convert text to speech with voice selection, multi-speaker support, and natural language style control using Gemini TTS

## Installation

### Using uvx (recommended)

```bash
uvx media-mcp
```

### Using pip

```bash
pip install media-mcp
```

### Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Configuration

Set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for authentication |
| `MEDIA_OUTPUT_DIR` | No | Directory path for saving generated media files (see below) |

### Output behavior

When `MEDIA_OUTPUT_DIR` is set, every generated file is saved to that directory and the tool returns **only the file path** — no binary data is included in the response. This is the recommended setup because MCP messages are stored in the conversation history, and large base64 payloads pollute context and waste tokens.

When `MEDIA_OUTPUT_DIR` is **not** set, the server has no filesystem target, so it returns the raw base64-encoded data directly in the response. This works for quick experiments but is not recommended for production use.

## MCP Client Setup

### Claude Desktop

Add to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "media-mcp": {
      "command": "uvx",
      "args": ["media-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key",
        "MEDIA_OUTPUT_DIR": "/path/to/media/output"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add media-mcp --transport stdio -- uvx media-mcp
```

Or add manually to `.mcp.json`:

```json
{
  "mcpServers": {
    "media-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["media-mcp"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}",
        "MEDIA_OUTPUT_DIR": "/path/to/media/output"
      }
    }
  }
}
```

## Tools

### `generate_image`

Generate or edit images using Gemini's Nano Banana models.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description of the image to generate |
| `model` | enum | No | `nano-banana-2` | `nano-banana-2`, `nano-banana-pro`, `nano-banana` |
| `aspect_ratio` | enum | No | `1:1` | `1:1`, `9:16`, `16:9`, `3:2`, `4:3`, and more |
| `image_size` | enum | No | `1K` | `512px`, `1K`, `2K`, `4K` |
| `reference_images` | list[str] | No | — | Base64-encoded reference images |
| `thinking_level` | enum | No | `minimal` | `minimal`, `high` |
| `use_google_search` | bool | No | `false` | Enable Google Search grounding |

**Example prompt**: "A watercolor painting of a cozy cabin in the mountains during autumn"

### `generate_video`

Generate videos with native audio using Veo models.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description including dialogue, sound effects, camera directions |
| `model` | enum | No | `veo-3.1` | `veo-3.1`, `veo-3` |
| `aspect_ratio` | enum | No | `16:9` | `16:9` (landscape), `9:16` (portrait) |
| `resolution` | enum | No | — | `720p`, `1080p`, `4K` |
| `first_frame_image` | str | No | — | Base64-encoded image for first frame |
| `last_frame_image` | str | No | — | Base64-encoded image for last frame |
| `reference_images` | list[str] | No | — | Up to 3 base64-encoded reference images |

**Example prompt**: "A slow dolly shot through a neon-lit alley at night, rain falling, 'Where are you going?' whispered softly, footsteps echoing"

### `generate_music`

Generate instrumental music using Lyria RealTime with weighted prompts.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompts` | list[dict] | Yes | — | Weighted prompts, e.g. `[{"text": "minimal techno", "weight": 1.0}]` |
| `bpm` | int | No | — | Tempo in beats per minute |
| `temperature` | float | No | `1.0` | Randomness/creativity control |
| `scale` | str | No | — | Musical scale constraint (e.g. `C_MAJOR_A_MINOR`) |
| `duration_seconds` | int | No | `30` | Duration of the output clip |

**Example prompts**: `[{"text": "Piano", "weight": 2.0}, {"text": "Meditation", "weight": 0.5}]`

### `generate_speech`

Convert text to speech with voice and style control.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | — | Text to speak. For multi-speaker, format as dialogue with speaker names. |
| `model` | enum | No | `flash-tts` | `flash-tts`, `pro-tts` |
| `voice_name` | str | No | — | Voice name: `Kore`, `Puck`, `Charon`, `Fenrir`, `Aoede`, `Leda`, `Orus`, `Zephyr` |
| `multi_speaker` | bool | No | `false` | Enable multi-speaker mode |
| `speakers` | list[dict] | No | — | Speaker-to-voice mapping, e.g. `[{"name": "Alice", "voice_name": "Kore"}]` |
| `style_instructions` | str | No | — | Style guidance, e.g. "Read in a calm, slow pace" |

**Example**: Text: "Welcome to the show!" with `voice_name: "Kore"` and `style_instructions: "Say cheerfully"`

## Troubleshooting

### "GEMINI_API_KEY environment variable is not set"

Set the environment variable before starting the server:

```bash
export GEMINI_API_KEY="your-key-here"
```

When using Claude Desktop or Claude Code, pass the key via the `env` block in your MCP configuration (see [MCP Client Setup](#mcp-client-setup)).

### "Authentication failed" or 401 errors

Your API key may be invalid or expired. Verify it at [Google AI Studio](https://aistudio.google.com/apikey).

### "Rate limit or quota exceeded" or 429 errors

Wait a moment and retry. Check your API quota at [Google AI Studio](https://aistudio.google.com/apikey).

### "Content blocked by safety filter"

Modify your prompt to avoid restricted content. The Gemini API applies safety filters to all generated media.

### Python version errors

media-mcp requires Python 3.10 or later. Check your version:

```bash
python --version
```

## License

MIT
