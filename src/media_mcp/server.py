from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from google import genai
from mcp.server.fastmcp import FastMCP

from media_mcp.config import ServerConfig, load_config


@dataclass
class AppContext:
    client: genai.Client
    config: ServerConfig


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    config = load_config()
    client = genai.Client(api_key=config.gemini_api_key)
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
    mcp.run()


if __name__ == "__main__":
    main()
