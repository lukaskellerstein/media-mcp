# Contract: MCP Client Configuration

**Branch**: `002-stdio-uvx-readme` | **Date**: 2026-03-13

This contract defines the configuration interface between the media-mcp server and MCP clients. Users copy these JSON structures into their client configuration to connect to the server.

## Claude Desktop Configuration

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

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

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | yes | Must be `"uvx"` |
| `args` | string[] | yes | Must include `"media-mcp"` as first element |
| `env` | object | yes | Must include `GEMINI_API_KEY` |
| `env.GEMINI_API_KEY` | string | yes | Valid Google Gemini API key |

## Claude Code Configuration

### Option A: CLI Command

```bash
claude mcp add media-mcp --transport stdio -- uvx media-mcp
```

### Option B: Manual `.mcp.json`

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

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | Must be `"stdio"` |
| `command` | string | yes | Must be `"uvx"` |
| `args` | string[] | yes | Must include `"media-mcp"` as first element |
| `env` | object | recommended | Supports `${VAR}` syntax for environment variable expansion |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | yes | Google Gemini API key for authentication |
| `MEDIA_OUTPUT_DIR` | no | Directory path for saving generated media files |

## Server Entry Point

The `media-mcp` command starts a FastMCP server communicating over stdio (stdin/stdout). The server:
1. Reads configuration from environment variables
2. Validates the API key (fails fast with actionable error if missing)
3. Exposes 4 tools: `generate_image_nano_banana`, `generate_video`, `generate_music`, `generate_speech`
4. Communicates using the MCP protocol over stdio
