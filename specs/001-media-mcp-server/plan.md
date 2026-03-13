# Implementation Plan: Media MCP Server

**Branch**: `001-media-mcp-server` | **Date**: 2026-03-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-media-mcp-server/spec.md`

## Summary

Build a Python MCP server that exposes four Google Gemini media
generation APIs (image, speech, video, music) as tools for AI agents.
The server uses the `mcp` Python SDK (FastMCP) for MCP protocol
handling and `google-genai` for all Gemini API interactions. It
supports stdio transport, validates all inputs, surfaces all upstream
errors clearly, and optionally saves generated media to a configurable
output directory.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: `mcp` (FastMCP server SDK), `google-genai`
(Gemini API client), `pydantic` (input validation)
**Storage**: Filesystem only (optional output directory for media files)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux server (also macOS for local development)
**Project Type**: MCP server (stdio tool server for AI agents)
**Performance Goals**: Image < 30s, Speech < 15s, Video < 5min,
Music < 60s (upstream API dependent)
**Constraints**: Stateless server, single API key, no persistent
storage
**Scale/Scope**: Single-user local server (one agent connection at a
time via stdio)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | Single flat package, no abstractions beyond tool-per-file. No ORM, no database, no caching layer. |
| II. SOLID Architecture | PASS | Each tool in its own module (SRP). Tools depend on genai.Client abstraction (DI via lifespan). Composition only, no inheritance. |
| III. Clean Code | PASS | Small focused functions. Tool handlers delegate to Gemini client. Pydantic for validation. |
| IV. Fail Fast | PASS | Input validation via Pydantic before API calls. All Gemini errors caught and surfaced with category + actionable message. |
| V. Tech Stack Discipline | PASS | Python only, managed via `uv`. Dependencies: `mcp`, `google-genai`, `pydantic`. No Node.js, no Go. |
| VI. Test and Verify | PASS | pytest for unit tests. Type hints throughout. Config via env vars. |
| VII. Zero Waste | PASS | Greenfield project — no dead code to accumulate. Linting enforced. |

No violations. Complexity Tracking section not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-media-mcp-server/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── mcp-tools.md     # MCP tool schemas
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/media_mcp/
├── __init__.py
├── server.py            # FastMCP server, lifespan, tool registration
├── config.py            # ServerConfig (Pydantic settings)
├── tools/
│   ├── __init__.py
│   ├── image.py         # generate_image tool
│   ├── speech.py        # generate_speech tool
│   ├── video.py         # generate_video tool
│   └── music.py         # generate_music tool
└── utils/
    ├── __init__.py
    ├── audio.py          # WAV header construction
    └── media.py          # File saving, base64 encoding helpers

tests/
├── __init__.py
├── conftest.py          # Shared fixtures (mock client, config)
├── test_config.py
├── test_image.py
├── test_speech.py
├── test_video.py
└── test_music.py

pyproject.toml           # Project metadata, dependencies, entry point
```

**Structure Decision**: Single-project flat layout. This is a
single-purpose MCP server with no frontend, no database, and no
multi-service architecture. Each tool gets its own module under
`tools/` for SRP. Shared utilities are minimal (audio helpers, file
saving). This is the simplest structure that supports all four tools
while keeping each independently testable.

## Key Design Decisions

### 1. Lifespan for Shared State

The `google-genai` client is initialized once at server startup via
FastMCP's lifespan pattern and shared across all tool calls. This
avoids creating a new client per request and ensures the API key is
validated once.

### 2. Tool Parameter Models

Each tool defines its parameters as a Pydantic model (or typed
function signature). FastMCP auto-generates the JSON schema for MCP
tool discovery. This gives us free input validation + schema
generation.

### 3. Model Name Mapping

Tools accept user-friendly model names (`nano-banana-2`, `veo-3.1`,
`flash-tts`) and map them internally to the actual Gemini model
identifiers (`gemini-3.1-flash-image-preview`, etc.). This decouples
the agent-facing interface from upstream model naming.

### 4. Error Handling Strategy

All Gemini API calls are wrapped in try/except that catches specific
error types and maps them to descriptive MCP error responses with:
- Error category (auth, validation, rate_limit, safety, timeout)
- Actionable message (what to fix or when to retry)
- Upstream details when available

### 5. Binary Data Return

- Images: returned via MCP SDK's `Image` type (base64 PNG)
- Audio (speech/music): returned via MCP `AudioContent` type
  (base64-encoded WAV with mimeType `audio/wav`)
- Video: MCP has no native video content type — return file path
  via `TextContent` (video must be saved to output_dir); if no
  output_dir, return base64 via `EmbeddedResource`
- If `output_dir` configured: all media also saved to disk with path
  returned

### 6. Video Async Polling

Video generation uses `asyncio.sleep()` in a poll loop (not
`time.sleep()`) to avoid blocking the event loop. Timeout is enforced
at 5 minutes.

### 7. Music WebSocket Session

Music generation opens a WebSocket session, collects audio chunks,
and returns the assembled WAV. Session cleanup is guaranteed via
async context manager.

## Complexity Tracking

> No violations — this section is intentionally empty.
