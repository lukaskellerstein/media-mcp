# Tasks: Media MCP Server

**Input**: Design documents from `/specs/001-media-mcp-server/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/mcp-tools.md

**Tests**: Not explicitly requested in the specification. Test tasks are not included.

**Organization**: Tasks are grouped by user story. US5 (Server Setup) is foundational and maps to Phase 2. US1-US4 map to Phases 3-6 in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/media_mcp/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [X] T001 Create directory structure per plan: `src/media_mcp/`, `src/media_mcp/tools/`, `src/media_mcp/utils/`, `tests/`
- [X] T002 Create `pyproject.toml` with project metadata (name: `media-mcp`, version: `0.1.0`, requires-python: `>=3.10`), dependencies (`mcp[cli]`, `google-genai`, `pydantic>=2.0`), entry point (`media-mcp = "media_mcp.server:main"`), build-system (`setuptools`, not hatchling)
- [X] T003 [P] Create all `__init__.py` files: `src/media_mcp/__init__.py`, `src/media_mcp/tools/__init__.py`, `src/media_mcp/utils/__init__.py`, `tests/__init__.py`

---

## Phase 2: Foundational — Server Setup & Configuration (US5, Priority: P1)

**Purpose**: Core server infrastructure that MUST be complete before ANY tool can be implemented

**Maps to**: User Story 5 (Server Setup and Configuration)

**⚠️ CRITICAL**: No tool implementation can begin until this phase is complete

- [X] T004 Implement `ServerConfig` Pydantic model in `src/media_mcp/config.py` — reads `GEMINI_API_KEY` (required, non-empty) and `MEDIA_OUTPUT_DIR` (optional, validates writable path) from environment variables. Fail fast with clear error if API key missing.
- [X] T005 [P] Implement WAV file construction utilities in `src/media_mcp/utils/audio.py` — two functions: `pcm_to_wav_speech(data: bytes) -> bytes` (24kHz, mono, 16-bit) and `pcm_to_wav_music(data: bytes) -> bytes` (48kHz, stereo, 16-bit). Use stdlib `wave` module.
- [X] T006 [P] Implement media file helpers in `src/media_mcp/utils/media.py` — `save_media_file(data: bytes, output_dir: str, filename: str) -> str` (saves file, returns absolute path), `encode_base64(data: bytes) -> str` (base64 encode for MCP responses), `generate_filename(tool_name: str, extension: str) -> str` (timestamp-based unique filename).
- [X] T007 Implement FastMCP server skeleton in `src/media_mcp/server.py` — create `FastMCP("media-mcp")` instance, implement async lifespan that initializes `genai.Client(api_key=config.gemini_api_key)` and yields it as shared context, implement `main()` function that calls `mcp.run()`. Include a helper function `handle_gemini_error(e: Exception) -> str` that maps Gemini API exceptions to categorized error messages (auth, rate_limit, safety, timeout, connection).

**Checkpoint**: Server starts via `uv run media-mcp`, accepts stdio connections, lists zero tools. Config errors shown clearly if API key missing.

---

## Phase 3: User Story 1 — Generate Images from Text (Priority: P1) 🎯 MVP

**Goal**: An agent can generate images from text prompts with full parameter control

**Independent Test**: Start server, call `generate_image` with `{"prompt": "A red circle on white background"}` via MCP Inspector, verify PNG image returned

### Implementation for User Story 1

- [X] T008 [US1] Implement `generate_image` tool in `src/media_mcp/tools/image.py` — define model name mapping (`nano-banana-2` → `gemini-3.1-flash-image-preview`, `nano-banana-pro` → `gemini-3-pro-image-preview`, `nano-banana` → `gemini-2.5-flash-image`), build `GenerateContentConfig` with `ImageConfig` (aspect_ratio, image_size) and `ThinkingConfig` (thinking_level), decode base64 reference images to PIL Image objects and pass in contents list, call `client.models.generate_content()`, parse response parts (extract `inline_data` for images, `text` for text), return MCP `Image` content + optional `TextContent`, save to output_dir via `utils/media.py` if configured, handle errors via `handle_gemini_error`. Export a `register(mcp, get_client)` function.
- [X] T009 [US1] Wire image tool into server — add `from media_mcp.tools.image import register as register_image` and call `register_image(mcp, get_client)` in `src/media_mcp/server.py`

**Checkpoint**: Agent can generate images via `generate_image` tool. All image parameters (model, aspect_ratio, image_size, reference_images, thinking_level, search grounding) functional. Errors surfaced clearly.

---

## Phase 4: User Story 2 — Generate Speech from Text (Priority: P2)

**Goal**: An agent can convert text to spoken audio with voice and style control

**Independent Test**: Call `generate_speech` with `{"text": "Hello world"}` via MCP Inspector, verify WAV audio returned

### Implementation for User Story 2

- [X] T010 [US2] Implement `generate_speech` tool in `src/media_mcp/tools/speech.py` — define model mapping (`flash-tts` → `gemini-2.5-flash-preview-tts`, `pro-tts` → `gemini-2.5-pro-preview-tts`), build `GenerateContentConfig` with `response_modalities=["AUDIO"]` and `SpeechConfig`/`VoiceConfig`/`PrebuiltVoiceConfig` for single-speaker, build `MultiSpeakerVoiceConfig` with `SpeakerVoiceConfig` entries when `multi_speaker=true`, prepend `style_instructions` to text content when provided, call `client.models.generate_content()`, extract PCM audio from `response.candidates[0].content.parts[0].inline_data.data`, convert to WAV via `utils/audio.py` `pcm_to_wav_speech()`, return as MCP `AudioContent` (base64, mimeType `audio/wav`) + file path if output_dir configured, handle errors. Export `register(mcp, get_client)`.
- [X] T011 [US2] Wire speech tool into server — add import and register call in `src/media_mcp/server.py`

**Checkpoint**: Agent can generate speech. Single-speaker, multi-speaker, voice selection, and style instructions all functional.

---

## Phase 5: User Story 3 — Generate Videos from Text or Images (Priority: P3)

**Goal**: An agent can generate video clips from text/images with async completion

**Independent Test**: Call `generate_video` with `{"prompt": "A sunset over the ocean"}` via MCP Inspector, verify MP4 file path returned after async wait

### Implementation for User Story 3

- [X] T012 [US3] Implement `generate_video` tool in `src/media_mcp/tools/video.py` — define model mapping (`veo-3.1` → `veo-3.1-generate-preview`, `veo-3` → `veo-3.0-generate-preview`), build `GenerateVideosConfig` (aspect_ratio, resolution, last_frame, reference_images as `VideoGenerationReferenceImage`), decode base64 first_frame_image and pass as `image=` param, handle `extend_video_id` by passing `video=` param, call `client.models.generate_videos()`, implement async polling loop with `asyncio.sleep(10)` and `client.operations.get(operation)` until `operation.done`, enforce 5-minute timeout, download result via `operation.response.generated_videos[0].video`, save MP4 to output_dir (required for video — return error if no output_dir and file too large for base64), return file path as `TextContent` or base64 via `EmbeddedResource`, use `ctx.report_progress()` during polling, handle errors. Export `register(mcp, get_client)`.
- [X] T013 [US3] Wire video tool into server — add import and register call in `src/media_mcp/server.py`

**Checkpoint**: Agent can generate videos. Text-to-video, image-to-video (first/last frame), reference images, video extension, and resolution control all functional. Timeout enforced.

---

## Phase 6: User Story 4 — Generate Music from Prompts (Priority: P4)

**Goal**: An agent can generate instrumental music from weighted text prompts

**Independent Test**: Call `generate_music` with `{"prompts": [{"text": "ambient piano", "weight": 1.0}], "duration_seconds": 10}` via MCP Inspector, verify WAV audio returned

### Implementation for User Story 4

- [X] T014 [US4] Implement `generate_music` tool in `src/media_mcp/tools/music.py` — connect via `client.aio.live.music.connect(model="models/lyria-realtime-exp")` as async context manager, call `session.set_weighted_prompts()` with `WeightedPrompt` objects from input, call `session.set_music_generation_config()` with `LiveMusicGenerationConfig` (bpm, temperature, scale mapped to `types.Scale` enum, guidance=4.0 default), call `session.play()`, collect audio chunks via `async for msg in session.receive()` into bytearray, stop after `duration_seconds` elapsed or session ends, convert accumulated PCM to WAV via `utils/audio.py` `pcm_to_wav_music()`, return as MCP `AudioContent` (base64, mimeType `audio/wav`) + file path if output_dir configured, guarantee session cleanup in finally block, handle WebSocket errors. Export `register(mcp, get_client)`.
- [X] T015 [US4] Wire music tool into server — add import and register call in `src/media_mcp/server.py`

**Checkpoint**: Agent can generate music. Weighted prompts, tempo, scale, temperature, and duration control all functional. Session cleanup guaranteed on error.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation and cleanup across all tools

- [X] T016 Verify all four tools discoverable via `uv run mcp dev src/media_mcp/server.py` — run MCP Inspector, confirm `generate_image`, `generate_speech`, `generate_video`, `generate_music` listed with correct parameter schemas matching contracts/mcp-tools.md
- [X] T017 [P] Validate error handling across all tools — test auth failure (invalid key), confirm rate limit and safety filter errors include category and actionable guidance, verify timeout behavior on video generation
- [X] T018 [P] Run quickstart.md validation — follow every step in specs/001-media-mcp-server/quickstart.md from scratch (setup, config, run, verify), confirm all steps work
- [X] T019 Code cleanup — verify no unused imports, consistent type hints on all public functions, no dead code, no commented-out code, linter passes clean

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (different files, independent tools)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 — Image (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 — Speech (P2)**: Can start after Phase 2 — no dependencies on other stories, uses shared `utils/audio.py`
- **US3 — Video (P3)**: Can start after Phase 2 — no dependencies on other stories
- **US4 — Music (P4)**: Can start after Phase 2 — no dependencies on other stories, uses shared `utils/audio.py`

### Within Each User Story

- Implementation task first (tool module)
- Wire task second (server.py registration)
- Each wire task touches `server.py` — these CANNOT run in parallel across stories

### Parallel Opportunities

- Phase 1: T003 can run in parallel with T001/T002
- Phase 2: T005 and T006 can run in parallel (different files)
- Phases 3-6: Tool implementation tasks (T008, T010, T012, T014) can run in parallel — each in a different file
- Phase 7: T017 and T018 can run in parallel

---

## Parallel Example: All Tool Implementations

```bash
# After Phase 2 is complete, launch all tool implementations together:
Task: "Implement generate_image in src/media_mcp/tools/image.py"
Task: "Implement generate_speech in src/media_mcp/tools/speech.py"
Task: "Implement generate_video in src/media_mcp/tools/video.py"
Task: "Implement generate_music in src/media_mcp/tools/music.py"

# Then wire all tools sequentially (all touch server.py):
Task: "Wire image tool into server.py"
Task: "Wire speech tool into server.py"
Task: "Wire video tool into server.py"
Task: "Wire music tool into server.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (server skeleton + config)
3. Complete Phase 3: User Story 1 (image generation)
4. **STOP and VALIDATE**: Generate an image via MCP Inspector
5. Server is usable — agents can generate images

### Incremental Delivery

1. Setup + Foundational → Server starts, zero tools
2. Add Image (US1) → Test independently → MVP!
3. Add Speech (US2) → Test independently → Two tools
4. Add Video (US3) → Test independently → Three tools
5. Add Music (US4) → Test independently → Full feature set
6. Polish → Validated and clean

### Parallel Strategy

1. Complete Setup + Foundational together
2. Once Foundational is done, implement all four tool modules in parallel
3. Wire tools into server.py sequentially
4. Polish and validate

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- All tool modules reference `research.md` for exact API call patterns
- All tool parameter schemas reference `contracts/mcp-tools.md`
- All entity structures reference `data-model.md`
- Wire tasks (T009, T011, T013, T015) are small — each adds one import + register call to server.py
- Commit after each phase or logical group
- Stop at any checkpoint to validate independently
