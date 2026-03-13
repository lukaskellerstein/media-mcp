from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, field_validator


class ServerConfig(BaseModel):
    gemini_api_key: str
    output_dir: str | None = None

    @field_validator("gemini_api_key")
    @classmethod
    def api_key_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(
                "GEMINI_API_KEY must not be empty. "
                "Set the GEMINI_API_KEY environment variable."
            )
        return v.strip()

    @field_validator("output_dir")
    @classmethod
    def output_dir_writable(cls, v: str | None) -> str | None:
        if v is None:
            return None
        path = Path(v)
        if not path.is_dir():
            raise ValueError(
                f"MEDIA_OUTPUT_DIR '{v}' is not an existing directory."
            )
        if not os.access(path, os.W_OK):
            raise ValueError(
                f"MEDIA_OUTPUT_DIR '{v}' is not writable."
            )
        return str(path.resolve())


def load_config() -> ServerConfig:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    output_dir = os.environ.get("MEDIA_OUTPUT_DIR")
    if not api_key:
        raise SystemExit(
            "Error: GEMINI_API_KEY environment variable is not set.\n"
            "Set it with: export GEMINI_API_KEY='your-key-here'"
        )
    return ServerConfig(gemini_api_key=api_key, output_dir=output_dir)
