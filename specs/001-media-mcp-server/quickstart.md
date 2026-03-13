# Quickstart: Media MCP Server

## Prerequisites

- Python 3.10+
- `uv` package manager
- A Google Gemini API key

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd media-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync
```

## Configuration

Set your Gemini API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Optionally set an output directory for saving generated media:

```bash
export MEDIA_OUTPUT_DIR="/path/to/output"
```

## Running the Server

### Stdio mode (default — for local agent use)

```bash
uv run media-mcp
```

### Development mode (with MCP inspector)

```bash
uv run mcp dev src/media_mcp/server.py
```

## Using with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "media-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/media-mcp", "run", "media-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Verifying It Works

1. Start the server in dev mode: `uv run mcp dev src/media_mcp/server.py`
2. In the MCP inspector, list available tools — you should see:
   - `generate_image`
   - `generate_speech`
   - `generate_video`
   - `generate_music`
3. Call `generate_image` with `{"prompt": "A red circle on a white
   background"}` — you should get back image data.

## Tool Quick Reference

| Tool | Required Param | What it does |
|------|---------------|--------------|
| `generate_image` | `prompt` | Generate images from text |
| `generate_speech` | `text` | Convert text to spoken audio |
| `generate_video` | `prompt` | Generate video clips from text |
| `generate_music` | `prompts` | Generate instrumental music |

See `specs/001-media-mcp-server/contracts/mcp-tools.md` for full
parameter schemas.
