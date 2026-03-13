# Implementation Plan: stdio Transport, uvx Installation & Project Documentation

**Branch**: `002-stdio-uvx-readme` | **Date**: 2026-03-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-stdio-uvx-readme/spec.md`

## Summary

Make media-mcp installable via `uvx media-mcp` with stdio as the primary transport, create a comprehensive README.md for onboarding, and set the GitHub repository description and topics. The server already supports stdio and has the correct entry point — the work is primarily packaging metadata, documentation, and GitHub configuration.

## Technical Context

**Language/Version**: Python 3.10+ (already configured)
**Primary Dependencies**: mcp[cli]>=1.0.0, google-genai, pydantic>=2.0 (already configured)
**Storage**: Filesystem only (optional output directory for media files)
**Testing**: Manual verification (run `uvx media-mcp` and connect from MCP client)
**Target Platform**: Linux, macOS, Windows (any platform with Python 3.10+ and uv)
**Project Type**: CLI tool / MCP server
**Performance Goals**: N/A (documentation and packaging feature)
**Constraints**: Must not use hatchling (constitution constraint)
**Scale/Scope**: Single package, 4 tools exposed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | No new abstractions. Minimal changes to existing code. |
| II. SOLID Architecture | PASS | No architectural changes. |
| III. Clean Code | PASS | README follows clear structure. No code duplication. |
| IV. Fail Fast | PASS | API key validation already implemented with clear error messages. |
| V. Technology Stack Discipline | PASS | Using setuptools (not hatchling). Python-only. uv for package management. |
| VI. Test and Verify | PASS | Manual verification via `uvx media-mcp` and MCP client connection. |
| VII. Zero Waste | PASS | No dead code. All additions serve a purpose. |

**Constitution Check (post-design)**: All gates still pass. No violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/002-stdio-uvx-readme/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── mcp-client-config.md  # MCP client configuration contract
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── media_mcp/
    ├── __init__.py
    ├── server.py          # Entry point (main function, unchanged)
    ├── config.py           # Configuration loading (unchanged)
    ├── tools/
    │   ├── __init__.py
    │   ├── image.py
    │   ├── video.py
    │   ├── music.py
    │   └── speech.py
    └── utils/
        ├── __init__.py
        ├── media.py
        └── audio.py

tests/
└── __init__.py

pyproject.toml             # UPDATE: add PyPI metadata (readme, license, authors, classifiers, urls)
README.md                  # NEW: comprehensive project documentation
```

**Structure Decision**: Existing `src/` layout with `setuptools` package discovery. No structural changes needed. Only `pyproject.toml` gets metadata additions and `README.md` is created at repository root.

## Implementation Approach

### Phase 1: Package Metadata (pyproject.toml)

Add PyPI-recommended metadata fields to `pyproject.toml`:
- `readme = "README.md"` — renders on PyPI
- `license` — MIT or appropriate license
- `authors` — package author
- `classifiers` — PyPI trove classifiers
- `keywords` — search terms
- `[project.urls]` — Homepage, Repository, Issues links

No changes to build system, dependencies, or entry point (all already correct).

### Phase 2: README.md Creation

Create `README.md` with these sections (in order):
1. Project name + badges + one-line description
2. Features list (4 tools with brief descriptions)
3. Installation (`uvx media-mcp` primary, `pip install media-mcp` secondary)
4. Configuration (GEMINI_API_KEY setup)
5. MCP client setup (Claude Desktop JSON snippet, Claude Code CLI command)
6. Tool reference (each tool: purpose, key parameters, example prompts)
7. Environment variables reference
8. Troubleshooting

Content sources: GOAL.md (tool descriptions), contracts/mcp-client-config.md (config snippets), quickstart.md (installation flow).

### Phase 3: GitHub Repository Metadata

Using GitHub API (via `gh`):
- Set repository description: "MCP server for AI-powered media generation (images, videos, music, speech) using Google Gemini"
- Add topics: `mcp`, `mcp-server`, `gemini`, `google-gemini`, `media-generation`, `ai-tools`, `image-generation`, `video-generation`, `text-to-speech`, `music-generation`

### Phase 4: Verification

- Build package locally with `uv build`
- Verify `uvx` can install from local wheel
- Verify server starts and responds to MCP protocol messages
- Verify README renders correctly in markdown preview

## Complexity Tracking

No constitution violations. No complexity justifications needed.
