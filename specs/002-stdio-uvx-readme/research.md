# Research: stdio Transport, uvx Installation & Project Documentation

**Branch**: `002-stdio-uvx-readme` | **Date**: 2026-03-13

## R1: uvx Installation Requirements

**Decision**: Keep setuptools as build backend; current `pyproject.toml` is already uvx-compatible.

**Rationale**: The existing configuration has all required elements:
- `[project.scripts]` with `media-mcp = "media_mcp.server:main"` — creates the CLI entry point that `uvx` invokes
- `requires-python = ">=3.10"` — enforced by uv/uvx
- `mcp[cli]>=1.0.0` — provides FastMCP and protocol infrastructure
- `setuptools>=75.0` — proven, stable build backend

**Alternatives considered**:
- hatchling: Used by official MCP servers (mcp-server-git, mcp-server-fetch). Simpler config but no material benefit for this project. Switching would require removing `[tool.setuptools.packages.find]` and adding `[tool.hatch.build.targets.wheel]`. Constitution notes `hatchling.build` MUST NOT appear in pyproject.toml, so setuptools is the correct choice.
- flit: Too minimal for projects with `src/` layout.

## R2: stdio Transport Verification

**Decision**: No code changes needed. FastMCP's `mcp.run()` defaults to stdio transport.

**Rationale**: The current `server.py:main()` calls `mcp.run()` which starts a stdio server by default. This is the standard pattern used by all reference MCP servers. The `mcp[cli]` extra provides the `mcp` CLI tooling but the server entry point runs stdio directly.

**Alternatives considered**:
- Explicit `mcp.run(transport="stdio")` — unnecessary, stdio is the default. Adding it would be over-specification per YAGNI.

## R3: Claude Desktop Configuration Format

**Decision**: Use standard `mcpServers` format with `uvx` as command.

```json
{
  "mcpServers": {
    "media-mcp": {
      "command": "uvx",
      "args": ["media-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key"
      }
    }
  }
}
```

**Rationale**: This is the documented format for Claude Desktop. The `env` block passes environment variables to the subprocess. Config file location: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

## R4: Claude Code Configuration Format

**Decision**: Document both CLI and manual `.mcp.json` approaches.

**CLI approach**:
```bash
claude mcp add media-mcp --transport stdio -- uvx media-mcp
```

**Manual `.mcp.json`**:
```json
{
  "mcpServers": {
    "media-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["media-mcp"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

**Rationale**: Claude Code supports `${VAR}` syntax for environment variable expansion. The CLI command is simplest for users; the JSON is useful for version-controlled project configs.

## R5: README Structure for MCP Servers

**Decision**: Follow the established pattern from published MCP servers.

**Standard sections** (in order):
1. Project name + one-line description
2. Features / capabilities list
3. Installation (`uvx` primary, `pip` secondary)
4. Configuration (API key setup)
5. MCP client setup (Claude Desktop, Claude Code snippets)
6. Tool reference (each tool with purpose, parameters, examples)
7. Troubleshooting / FAQ

**Rationale**: Reviewed mcp-server-git, mcp-server-fetch, and Azure MCP Server patterns. This order matches user mental model: "What is it? → Can it do what I need? → How do I install it? → How do I use it?"

## R6: GitHub Repository Metadata

**Decision**: Set description and topics via GitHub API or UI.

**Description**: "MCP server for AI-powered media generation (images, videos, music, speech) using Google Gemini"

**Topics**: `mcp`, `mcp-server`, `gemini`, `google-gemini`, `media-generation`, `ai-tools`, `image-generation`, `video-generation`, `text-to-speech`, `music-generation`

**Rationale**: Topics improve GitHub search discoverability. The description appears in search results and repository cards.

## R7: pyproject.toml Enhancements for PyPI

**Decision**: Add optional but recommended metadata fields for PyPI listing.

Fields to add:
- `readme = "README.md"` — renders README on PyPI
- `license` — standard license identifier
- `authors` — package author info
- `classifiers` — PyPI trove classifiers for discoverability
- `[project.urls]` — Homepage, Repository, Issues links
- `keywords` — search terms

**Rationale**: These fields improve PyPI discoverability and present professionally. They are standard for published packages and cost nothing to add.
