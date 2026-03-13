from __future__ import annotations

import os
from unittest.mock import AsyncMock

import pytest
from google import genai

from media_mcp.config import ServerConfig
from media_mcp.server import AppContext, mcp as server_mcp


@pytest.fixture(scope="session")
def gemini_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        pytest.skip("GEMINI_API_KEY not set — skipping integration tests")
    return key


@pytest.fixture(scope="session")
def app_context(gemini_api_key: str) -> AppContext:
    client = genai.Client(api_key=gemini_api_key)
    config = ServerConfig(gemini_api_key=gemini_api_key)
    return AppContext(client=client, config=config)


@pytest.fixture()
def app_context_with_output_dir(gemini_api_key: str, tmp_path) -> AppContext:
    """AppContext with output_dir set to a temp directory."""
    client = genai.Client(api_key=gemini_api_key)
    config = ServerConfig(gemini_api_key=gemini_api_key, output_dir=str(tmp_path))
    return AppContext(client=client, config=config)


@pytest.fixture()
def mock_ctx(app_context: AppContext) -> AsyncMock:
    ctx = AsyncMock()
    ctx.request_context.lifespan_context = app_context
    return ctx


@pytest.fixture()
def mock_ctx_with_output_dir(app_context_with_output_dir: AppContext) -> AsyncMock:
    """Mock context with MEDIA_OUTPUT_DIR configured."""
    ctx = AsyncMock()
    ctx.request_context.lifespan_context = app_context_with_output_dir
    return ctx


def get_tool_fn(name: str):
    """Get a registered tool function by name from the server's MCP instance."""
    for tool in server_mcp._tool_manager._tools.values():
        if tool.name == name:
            return tool.fn
    raise AssertionError(f"Tool '{name}' not registered")
