# Data Model: stdio Transport, uvx Installation & Project Documentation

**Branch**: `002-stdio-uvx-readme` | **Date**: 2026-03-13

This feature is primarily documentation and packaging — there are no new data entities to model. The existing data model is unchanged.

## Existing Entities (unchanged)

### ServerConfig
- `gemini_api_key: str` — API key for Gemini, read from `GEMINI_API_KEY` env var
- `output_dir: str | None` — optional directory for saving generated media, from `MEDIA_OUTPUT_DIR` env var

### AppContext
- `client: genai.Client` — authenticated Gemini API client
- `config: ServerConfig` — validated server configuration

## Configuration Artifacts (new)

### Package Metadata (pyproject.toml)
Not a data entity but a configuration artifact that defines:
- Package identity: name, version, description
- Distribution metadata: authors, license, classifiers, URLs
- Entry point: `media-mcp` CLI command
- Dependencies: runtime requirements

### MCP Client Configuration (JSON snippets)
Documented configuration structures for MCP clients:
- Claude Desktop: `claude_desktop_config.json` with `mcpServers` block
- Claude Code: `.mcp.json` with `mcpServers` block (or CLI command)

Both reference the same server entry point (`uvx media-mcp`) and pass `GEMINI_API_KEY` via environment.
