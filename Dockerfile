# syntax=docker/dockerfile:1

# ---- build stage: resolve deps + install the package into a venv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
# Frozen, prod-only, non-editable install → self-contained /app/.venv with the
# `media-mcp` console script on PATH.
RUN uv sync --frozen --no-dev --no-editable

# ---- runtime stage: slim, non-root ----
FROM python:3.12-slim AS runtime
RUN useradd -u 1000 -m app
COPY --from=build --chown=1000:1000 /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    MEDIA_MCP_TRANSPORT=streamable-http \
    MEDIA_MCP_HOST=0.0.0.0 \
    MEDIA_MCP_PORT=8000
# Deployed as a shared streamable-HTTP service. Leave MEDIA_OUTPUT_DIR UNSET so
# tools return media inline (base64) — a remote caller cannot read a path written
# on this container's filesystem.
USER 1000
EXPOSE 8000
ENTRYPOINT ["media-mcp"]
