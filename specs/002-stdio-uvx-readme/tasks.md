# Tasks: stdio Transport, uvx Installation & Project Documentation

**Input**: Design documents from `/specs/002-stdio-uvx-readme/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification. No test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup tasks needed. Project structure already exists with correct `src/` layout, dependencies, and entry point.

*(No tasks — project is already initialized)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational blocking tasks. The server already supports stdio transport via `mcp.run()`, has the correct entry point in `pyproject.toml`, and reads `GEMINI_API_KEY` from environment variables with proper error handling.

*(No tasks — all prerequisites already satisfied)*

---

## Phase 3: User Story 1 - Install and run via uvx (Priority: P1) MVP

**Goal**: Make the package installable and runnable via `uvx media-mcp` with proper PyPI metadata, so MCP clients can connect over stdio.

**Independent Test**: Run `uvx media-mcp` (or `uv run --from . media-mcp` locally) and verify the server starts and exposes all 4 tools over stdio.

### Implementation for User Story 1

- [x] T001 [US1] Add PyPI metadata fields to pyproject.toml: `readme`, `license`, `authors`, `keywords`, `classifiers`, and `[project.urls]` section (Homepage, Repository, Issues) per research.md R7. File: `pyproject.toml`
- [x] T002 [US1] Verify package builds successfully by running `uv build` and confirming a wheel is produced in `dist/`. File: `dist/`
- [x] T003 [US1] Verify the server starts via the entry point by running `uv run media-mcp` and confirming it enters stdio mode without errors (with `GEMINI_API_KEY` set). File: `src/media_mcp/server.py` (read-only verification)

**Checkpoint**: Package builds cleanly, entry point works, server starts in stdio mode. Ready for uvx distribution once published to PyPI.

---

## Phase 4: User Story 2 - README as primary onboarding guide (Priority: P2)

**Goal**: Create a comprehensive README.md that enables a new developer to install, configure, and use media-mcp in under 5 minutes.

**Independent Test**: A new user reads only the README, follows the instructions, and successfully connects media-mcp to their MCP client.

### Implementation for User Story 2

- [x] T004 [US2] Create README.md at repository root with project overview section: name, one-line description, and features list covering all 4 tools (image, video, music, speech). Content source: GOAL.md tool descriptions. File: `README.md`
- [x] T005 [US2] Add Installation section to README.md: primary method (`uvx media-mcp`), secondary method (`pip install media-mcp`), and prerequisites (Python 3.10+, uv, Gemini API key). Content source: quickstart.md. File: `README.md`
- [x] T006 [US2] Add Configuration section to README.md: `GEMINI_API_KEY` setup instructions, optional `MEDIA_OUTPUT_DIR` variable, and environment variable reference table. Content source: contracts/mcp-client-config.md. File: `README.md`
- [x] T007 [US2] Add MCP Client Setup section to README.md with copy-pasteable config snippets: Claude Desktop (`claude_desktop_config.json` JSON block), Claude Code (CLI command and `.mcp.json` JSON block). Content source: contracts/mcp-client-config.md. File: `README.md`
- [x] T008 [US2] Add Tools Reference section to README.md: each tool with purpose, key parameters table, and example prompt. Tools: `generate_image_nano_banana`, `generate_video`, `generate_music`, `generate_speech`. Content source: GOAL.md tool specifications. File: `README.md`
- [x] T009 [US2] Add Troubleshooting section to README.md covering: missing API key error, Python version mismatch, network connectivity issues, and safety filter blocks. File: `README.md`

**Checkpoint**: README.md is complete, covers all required sections (FR-004, FR-005), and renders correctly in markdown preview.

---

## Phase 5: User Story 3 - GitHub repository presents professionally (Priority: P3)

**Goal**: Set the GitHub repository description and topic tags so the project is discoverable and presents professionally.

**Independent Test**: Visit the GitHub repository page and verify the description and topics are visible.

### Implementation for User Story 3

- [x] T010 [US3] Set GitHub repository description to "MCP server for AI-powered media generation (images, videos, music, speech) using Google Gemini" using `gh repo edit` CLI command. Target: `lukaskellerstein/media-mcp`
- [x] T011 [US3] Add GitHub repository topics using `gh repo edit --add-topic` for: `mcp`, `mcp-server`, `gemini`, `google-gemini`, `media-generation`, `ai-tools`, `image-generation`, `video-generation`, `text-to-speech`, `music-generation`. Target: `lukaskellerstein/media-mcp`

**Checkpoint**: Repository page shows description and topics. Searchable via "MCP media generation" or "Gemini MCP server" on GitHub.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification across all user stories.

- [x] T012 Verify README.md renders correctly on GitHub by reviewing the rendered output (no broken formatting, tables, or code blocks)
- [x] T013 Verify all JSON config snippets in README.md are valid JSON and match the contract in specs/002-stdio-uvx-readme/contracts/mcp-client-config.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped — project already initialized
- **Foundational (Phase 2)**: Skipped — no blocking prerequisites
- **US1 (Phase 3)**: Can start immediately — updates pyproject.toml metadata
- **US2 (Phase 4)**: Can start immediately — creates README.md (independent file)
- **US3 (Phase 5)**: Can start immediately — GitHub API calls (no file dependencies)
- **Polish (Phase 6)**: Depends on US1 and US2 completion

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories. Independent.
- **User Story 2 (P2)**: No dependencies on other stories. References package name from pyproject.toml but that already exists.
- **User Story 3 (P3)**: No dependencies on other stories. Independent GitHub API calls.

### Within Each User Story

- **US1**: T001 (metadata) → T002 (build verify) → T003 (runtime verify) — sequential
- **US2**: T004 → T005 → T006 → T007 → T008 → T009 — sequential (same file)
- **US3**: T010 and T011 are sequential (same target)

### Parallel Opportunities

- **US1 (T001-T003) and US2 (T004-T009) and US3 (T010-T011)** can all run in parallel since they touch different files/targets:
  - US1: `pyproject.toml` + build verification
  - US2: `README.md`
  - US3: GitHub API

---

## Parallel Example: All User Stories

```bash
# All three user stories can execute simultaneously:

# Stream 1 (US1): Package metadata
Task: "Add PyPI metadata to pyproject.toml"
Task: "Verify package builds with uv build"
Task: "Verify server starts via entry point"

# Stream 2 (US2): Documentation
Task: "Create README.md with overview"
Task: "Add installation section"
Task: "Add configuration section"
Task: "Add MCP client setup section"
Task: "Add tools reference section"
Task: "Add troubleshooting section"

# Stream 3 (US3): GitHub metadata
Task: "Set repository description"
Task: "Add repository topics"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (pyproject.toml metadata + build verification)
2. **STOP and VALIDATE**: Run `uv build` and `uv run media-mcp` to confirm
3. Package is now uvx-ready (pending PyPI publish)

### Incremental Delivery

1. US1 → Package is uvx-installable (MVP!)
2. US2 → README provides onboarding documentation
3. US3 → Repository is discoverable on GitHub
4. Polish → Final verification across all stories

### Parallel Strategy

All 3 user stories can execute simultaneously since they modify different targets. Polish phase follows completion of US1 + US2.

---

## Notes

- No test tasks included (not requested in spec)
- No code changes to `src/` needed — server already supports stdio via `mcp.run()`
- All US2 tasks (T004-T009) modify the same file (`README.md`) so they must be sequential
- T002 and T003 are verification tasks, not implementation tasks — they validate that existing code works correctly with the new metadata
- Content for README sections should be sourced from GOAL.md and the contracts/ design document to maintain consistency
