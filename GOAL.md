
# media-MCP — Project Goal

## Overview

**media-MCP** is an MCP (Model Context Protocol) server that exposes Google's generative media APIs as tools for AI agents. It provides a unified interface for generating images, videos, music, and speech — all powered by the Gemini ecosystem.

The server accepts a `GEMINI_API_KEY` as a configuration parameter and exposes a set of tools that AI agents can invoke with fine-grained control over output quality, resolution, style, and other generation parameters.

---

## API Documentation References

| Capability | Docs |
|---|---|
| Image Generation (Nano Banana) | https://ai.google.dev/gemini-api/docs/image-generation |
| Video Generation (Veo) | https://ai.google.dev/gemini-api/docs/video |
| Music Generation (Lyria) | https://ai.google.dev/gemini-api/docs/music-generation |
| Speech Generation (TTS) | https://ai.google.dev/gemini-api/docs/speech-generation |

---

## Server Configuration

The MCP server is initialized with:

```json
{
  "gemini_api_key": "<GEMINI_API_KEY>"
}
```

All tools use this key to authenticate against `https://generativelanguage.googleapis.com/v1beta/`.

---

## Tools

### 1. `generate_image_nano_banana`

Generate or edit images using Gemini's native image generation (Nano Banana).

**When to use:** Conversational image creation/editing, multi-turn workflows, images with embedded text, infographics, interleaved text+image output.

**Models:**
- `gemini-3.1-flash-image-preview` — **Nano Banana 2** (high-efficiency, fast, high-volume)
- `gemini-3-pro-image-preview` — **Nano Banana Pro** (professional asset production, advanced reasoning/thinking)
- `gemini-2.5-flash-image` — **Nano Banana** (speed and efficiency, legacy)

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | yes | Text description of the image to generate |
| `model` | enum | no | `nano-banana-2` (default), `nano-banana-pro`, `nano-banana` |
| `aspect_ratio` | enum | no | `1:1` (default), `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9` |
| `image_size` | enum | no | `512px`, `1K` (default), `2K`, `4K` |
| `reference_images` | array of base64 | no | Up to 14 reference images (10 objects + 4 characters for 3.1 Flash; 6 objects + 5 characters for 3 Pro) |
| `response_modalities` | array | no | `["TEXT", "IMAGE"]` (default) or `["IMAGE"]` |
| `thinking_level` | enum | no | `minimal` (default for 3.1 Flash), `high` — controls reasoning depth |
| `use_google_search` | bool | no | Enable grounding with Google Search for real-time data |
| `use_image_search` | bool | no | Enable Google Image Search grounding (3.1 Flash only) |

**Output:** Base64-encoded PNG image(s) + optional text.


### 2. `generate_video`

Generate videos using Google's Veo model.

**When to use:** Text-to-video, image-to-video, video extension, and frame-specified generation.

**Models:**
- `veo-3.1-generate-preview` — **Veo 3.1** (state-of-the-art, 8s, 720p/1080p/4K, native audio with dialogue/sound effects)
- `veo-3.0-generate-preview` — **Veo 3** (native audio, dialogue)

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | yes | Text description of the video. Include dialogue in quotes, sound effects, camera directions, cinematic style. |
| `model` | enum | no | `veo-3.1` (default), `veo-3` |
| `aspect_ratio` | enum | no | `16:9` (default, landscape), `9:16` (portrait) |
| `resolution` | enum | no | `720p`, `1080p`, `4K` |
| `first_frame_image` | base64 | no | Image to use as the first frame |
| `last_frame_image` | base64 | no | Image to use as the last frame |
| `reference_images` | array of base64 | no | Up to 3 reference images for content guidance |
| `extend_video_id` | string | no | ID of a previously generated video to extend |

**Prompt tips for the agent:**
- Include dialogue in single quotes within the prompt
- Describe sound effects explicitly (e.g., "birds chirping", "rain on a window")
- Specify camera movements (e.g., "slow dolly in", "aerial tracking shot")
- Describe lighting and mood (e.g., "golden hour", "neon-lit alley")

**Output:** Video file (MP4). Generation is asynchronous — the tool polls until complete.


### 3. `generate_music`

Generate music using Google's Lyria RealTime model via a streaming WebSocket session.

**When to use:** Real-time instrumental music generation with interactive steering.

**Model:** `lyria-realtime-exp` (experimental)

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompts` | array of `{text, weight}` | yes | Weighted text prompts describing the music (e.g., `[{"text": "minimal techno", "weight": 1.0}]`) |
| `bpm` | int | no | Tempo in beats per minute (e.g., 90, 120) |
| `temperature` | float | no | Randomness/creativity (default: 1.0) |
| `scale` | enum | no | Musical scale constraint |
| `duration_seconds` | int | no | Desired duration of the output clip |
| `audio_format` | enum | no | `pcm16` (default) |
| `sample_rate_hz` | int | no | `44100` (default) |

**Prompt tips for the agent:**
- Combine genre + instrument + mood prompts with weights (e.g., `[{"text": "Piano", "weight": 2.0}, {"text": "Meditation", "weight": 0.5}]`)
- Use weight to emphasize or de-emphasize certain aspects
- For transitions, send intermediate weight values to avoid abrupt changes

**Output:** PCM audio stream (WAV). The tool manages the WebSocket session internally.

**Note:** Lyria RealTime is experimental and uses a streaming/WebSocket API (`v1alpha`), which differs from the standard REST pattern. The MCP server must manage connection lifecycle.


### 4. `generate_speech`

Generate speech from text using Gemini's TTS capabilities.

**When to use:** Podcast generation, audiobook narration, voiceovers, any scenario needing exact text recitation with style control.

**Models:**
- `gemini-2.5-flash-preview-tts` — Fast, single/multi-speaker TTS
- `gemini-2.5-pro-preview-tts` — Higher quality TTS

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `text` | string | yes | The text to speak. For multi-speaker, format as dialogue with speaker names. |
| `model` | enum | no | `flash-tts` (default), `pro-tts` |
| `voice_name` | string | no | Prebuilt voice name (e.g., `Kore`, `Puck`, `Charon`, `Fenrir`, `Aoede`, `Leda`, `Orus`, `Zephyr`) |
| `multi_speaker` | bool | no | Enable multi-speaker mode (up to 2 speakers) |
| `speakers` | array of `{name, voice_name}` | no | Speaker-to-voice mapping for multi-speaker mode |
| `style_instructions` | string | no | Natural language style guidance embedded in the prompt (e.g., "Say cheerfully:", "Read in a calm, slow pace:") |

**Style control (via prompt):** TTS is *controllable* — the agent can influence style, accent, pace, and tone by structuring the text prompt with natural language instructions.

**Output:** PCM audio data (24kHz, 16-bit, mono). Saved as WAV.

---

## Architecture Notes

### Transport
The MCP server should support **stdio** transport (for local agent use) and optionally **SSE** (for remote/web use).

### Async Operations
Video generation (Veo) is asynchronous. The server must:
1. Submit the generation request
2. Poll the operation status until `done == true`
3. Download the result and return it

Music generation (Lyria) uses WebSockets and requires session lifecycle management.

### File Handling
All generated media should be returned as:
- Base64-encoded data in the tool response, OR
- Saved to a configurable output directory with the file path returned

### Error Handling
- API rate limits and quota errors should be surfaced clearly
- Safety filter blocks should be reported with the filter category
- Timeout handling for long-running video generation

---

## Implementation Priorities

1. **Phase 1:** Image generation (Nano Banana) — most immediately useful
2. **Phase 2:** Speech generation (TTS) — straightforward REST API
3. **Phase 3:** Video generation (Veo) — async polling adds complexity
4. **Phase 4:** Music generation (Lyria) — experimental, WebSocket-based, most complex