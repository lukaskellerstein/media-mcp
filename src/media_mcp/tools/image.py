from __future__ import annotations

from typing import Literal

from google.genai import types
from mcp.server.fastmcp import Context, FastMCP, Image
from mcp.types import CallToolResult, TextContent

from media_mcp.server import AppContext, handle_gemini_error
from media_mcp.utils.media import (
    decode_base64,
    generate_filename,
    save_media_file,
)

MODEL_MAP = {
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "nano-banana-pro": "gemini-3-pro-image-preview",
    "nano-banana": "gemini-2.5-flash-image",
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_image(
        prompt: str,
        model: Literal["nano-banana-2", "nano-banana-pro", "nano-banana"] = "nano-banana-2",
        aspect_ratio: Literal[
            "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
            "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
        ] = "1:1",
        image_size: Literal["512px", "1K", "2K", "4K"] = "1K",
        reference_images: list[str] | None = None,
        response_modalities: list[Literal["TEXT", "IMAGE"]] | None = None,
        thinking_level: Literal["minimal", "high"] = "minimal",
        use_google_search: bool = False,
        use_image_search: bool = False,
        ctx: Context = None,
    ) -> CallToolResult:
        """Generate or edit images using Google's Gemini image generation models.

        Supports conversational image creation/editing, multi-turn workflows,
        images with embedded text, infographics, and interleaved text+image output.
        """
        app: AppContext = ctx.request_context.lifespan_context

        gemini_model = MODEL_MAP[model]
        modalities = response_modalities or ["TEXT", "IMAGE"]
        size_value = image_size.replace("px", "")

        config = types.GenerateContentConfig(
            response_modalities=modalities,
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=size_value,
            ),
        )

        if thinking_level == "high":
            config.thinking_config = types.ThinkingConfig(
                thinking_level="High",
            )

        contents: list = [prompt]
        if reference_images:
            for ref_b64 in reference_images:
                img_bytes = decode_base64(ref_b64)
                contents.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=img_bytes,
                        )
                    )
                )

        tools_config = None
        if use_google_search or use_image_search:
            tools_config = [types.Tool(google_search=types.GoogleSearch())]

        try:
            response = app.client.models.generate_content(
                model=gemini_model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=handle_gemini_error(e))],
                isError=True,
            )

        result_content = []
        image_data_for_save = None

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                result_content.append(
                    TextContent(type="text", text=part.text)
                )
            elif part.inline_data is not None:
                img_bytes = part.inline_data.data
                image_data_for_save = img_bytes
                result_content.append(
                    Image(data=img_bytes, format="png").to_image_content()
                )

        if app.config.output_dir and image_data_for_save:
            filename = generate_filename("image", "png")
            path = save_media_file(
                image_data_for_save, app.config.output_dir, filename
            )
            result_content.append(
                TextContent(type="text", text=f"Saved to: {path}")
            )

        return CallToolResult(content=result_content)
