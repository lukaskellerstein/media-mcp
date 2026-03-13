from __future__ import annotations

import asyncio
from typing import Literal

from google.genai import types
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, EmbeddedResource, TextContent

from media_mcp.server import AppContext, handle_gemini_error
from media_mcp.utils.media import (
    decode_base64,
    encode_base64,
    generate_filename,
    save_media_file,
)

MODEL_MAP = {
    "veo-3.1": "veo-3.1-generate-preview",
    "veo-3": "veo-3.0-generate-preview",
}

POLL_INTERVAL_SECONDS = 10
TIMEOUT_SECONDS = 300  # 5 minutes


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_video(
        prompt: str,
        model: Literal["veo-3.1", "veo-3"] = "veo-3.1",
        aspect_ratio: Literal["16:9", "9:16"] = "16:9",
        resolution: Literal["720p", "1080p", "4K"] | None = None,
        first_frame_image: str | None = None,
        last_frame_image: str | None = None,
        reference_images: list[str] | None = None,
        extend_video_id: str | None = None,
        ctx: Context = None,
    ) -> CallToolResult:
        """Generate videos from text prompts or reference images using Google's Veo models.

        Supports text-to-video, image-to-video, video extension, and
        frame-specified generation. Generation is asynchronous.
        """
        app: AppContext = ctx.request_context.lifespan_context

        gemini_model = MODEL_MAP[model]

        config_kwargs: dict = {
            "aspect_ratio": aspect_ratio,
        }
        if resolution:
            config_kwargs["resolution"] = resolution.lower()

        image_param = None
        if first_frame_image:
            img_bytes = decode_base64(first_frame_image)
            image_param = types.Image(image_bytes=img_bytes)

        if last_frame_image:
            last_bytes = decode_base64(last_frame_image)
            config_kwargs["last_frame"] = types.Image(image_bytes=last_bytes)

        if reference_images:
            refs = []
            for ref_b64 in reference_images[:3]:
                ref_bytes = decode_base64(ref_b64)
                refs.append(
                    types.VideoGenerationReferenceImage(
                        image=types.Image(image_bytes=ref_bytes),
                        reference_type="asset",
                    )
                )
            config_kwargs["reference_images"] = refs

        video_config = types.GenerateVideosConfig(**config_kwargs)

        generate_kwargs: dict = {
            "model": gemini_model,
            "prompt": prompt,
            "config": video_config,
        }
        if image_param:
            generate_kwargs["image"] = image_param

        try:
            operation = app.client.models.generate_videos(**generate_kwargs)
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=handle_gemini_error(e))],
                isError=True,
            )

        elapsed = 0
        try:
            while not operation.done:
                if elapsed >= TIMEOUT_SECONDS:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=(
                                "[timeout] Video generation timed out after "
                                f"{TIMEOUT_SECONDS}s. Try a simpler prompt or "
                                "lower resolution."
                            ),
                        )],
                        isError=True,
                    )
                await ctx.report_progress(
                    progress=elapsed,
                    total=TIMEOUT_SECONDS,
                )
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                elapsed += POLL_INTERVAL_SECONDS
                operation = app.client.operations.get(operation)
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=handle_gemini_error(e))],
                isError=True,
            )

        generated_video = operation.response.generated_videos[0]

        try:
            app.client.files.download(file=generated_video.video)
            video_bytes = generated_video.video.video_bytes
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=handle_gemini_error(e))],
                isError=True,
            )

        if app.config.output_dir:
            filename = generate_filename("video", "mp4")
            path = save_media_file(video_bytes, app.config.output_dir, filename)
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Video generated and saved to: {path}",
                )]
            )

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Video generated successfully. Data returned as base64.",
                ),
                EmbeddedResource(
                    type="resource",
                    resource={
                        "uri": f"data:video/mp4;base64,{encode_base64(video_bytes)}",
                        "mimeType": "video/mp4",
                        "text": encode_base64(video_bytes),
                    },
                ),
            ]
        )
