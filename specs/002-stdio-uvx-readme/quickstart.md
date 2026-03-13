# Quickstart: media-mcp

**Branch**: `002-stdio-uvx-readme` | **Date**: 2026-03-13

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

## 1. Set your API key

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

## 2. Run the server

```bash
uvx media-mcp
```

The server starts and communicates over stdio. It is now ready to receive MCP protocol messages.

## 3. Configure your MCP client

### Claude Desktop

Add to `claude_desktop_config.json`:

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

### Claude Code

```bash
claude mcp add media-mcp --transport stdio -- uvx media-mcp
```

## 4. Use the tools

Once configured, your AI agent can invoke:

- **generate_image_nano_banana** — Generate images from text prompts
- **generate_video** — Generate videos with audio from text prompts
- **generate_music** — Generate instrumental music from weighted prompts
- **generate_speech** — Convert text to speech with voice and style control

## Verify it works

Ask your AI agent: "Generate an image of a sunset over mountains" — if the server is configured correctly, it will use the `generate_image_nano_banana` tool to produce the image.
