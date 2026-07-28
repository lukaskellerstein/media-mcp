from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP

from media_mcp.config import ServerConfig, load_config


@dataclass
class AppContext:
    client: genai.Client
    config: ServerConfig


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    config = load_config()
    client = genai.Client(
        api_key=config.gemini_api_key,
        http_options=types.HttpOptions(timeout=config.request_timeout_ms),
    )
    yield AppContext(client=client, config=config)


mcp = FastMCP("media-mcp", lifespan=app_lifespan)


def handle_gemini_error(e: Exception) -> str:
    """Map Gemini API exceptions to categorized, actionable error messages."""
    error_str = str(e).lower()
    if "api key" in error_str or "authentication" in error_str or "401" in error_str:
        return (
            f"[auth] Authentication failed: {e}. "
            "Check that GEMINI_API_KEY is valid and has not expired."
        )
    if "quota" in error_str or "rate" in error_str or "429" in error_str:
        return (
            f"[rate_limit] Rate limit or quota exceeded: {e}. "
            "Wait a moment and retry, or check your API quota."
        )
    if "safety" in error_str or "blocked" in error_str or "filter" in error_str:
        return (
            f"[safety] Content blocked by safety filter: {e}. "
            "Modify your prompt to avoid restricted content."
        )
    if "timeout" in error_str or "deadline" in error_str:
        return (
            f"[timeout] Request timed out: {e}. "
            "The operation took too long. Try again or simplify your request."
        )
    if "connect" in error_str or "network" in error_str or "unreachable" in error_str:
        return (
            f"[connection] Connection error: {e}. "
            "Check your network connection and try again."
        )
    return f"[error] Gemini API error: {e}"


# Register tools — imports trigger @mcp.tool() registration
from media_mcp.tools.image import register as register_image  # noqa: E402
from media_mcp.tools.speech import register as register_speech  # noqa: E402
from media_mcp.tools.video import register as register_video  # noqa: E402
from media_mcp.tools.music import register as register_music  # noqa: E402

register_image(mcp)
register_speech(mcp)
register_video(mcp)
register_music(mcp)


def main() -> None:
    # Transport is selected by env so the same entrypoint serves both the local
    # stdio use case (default) and a networked deployment. For the streamable-HTTP
    # service, leave MEDIA_OUTPUT_DIR UNSET so tools return media inline (base64)
    # instead of a server-local file path the remote caller cannot read.
    transport = os.environ.get("MEDIA_MCP_TRANSPORT", "stdio").strip().lower()
    if transport in {"http", "streamable-http", "streamable_http"}:
        from mcp.server.transport_security import TransportSecuritySettings

        mcp.settings.host = os.environ.get("MEDIA_MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("MEDIA_MCP_PORT", "8000"))
        # FastMCP pins DNS-rebinding protection to a localhost-only allow-list at
        # construction time (when host still defaults to 127.0.0.1), which then
        # rejects the in-cluster Service hostname ("Invalid Host header"). This
        # service is a ClusterIP reached only from inside the cluster, so disable
        # the host check rather than maintain an allow-list of every caller.
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
