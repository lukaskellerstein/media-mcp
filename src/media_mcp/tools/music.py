from __future__ import annotations

import time

from google.genai import types
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import AudioContent, CallToolResult, TextContent

from media_mcp.server import AppContext, handle_gemini_error
from media_mcp.utils.audio import pcm_to_wav_music
from media_mcp.utils.media import (
    encode_base64,
    generate_filename,
    save_media_file,
)

SCALE_MAP = {
    "C_MAJOR_A_MINOR": types.Scale.C_MAJOR_A_MINOR,
    "D_FLAT_MAJOR_B_FLAT_MINOR": types.Scale.D_FLAT_MAJOR_B_FLAT_MINOR,
    "D_MAJOR_B_MINOR": types.Scale.D_MAJOR_B_MINOR,
    "E_FLAT_MAJOR_C_MINOR": types.Scale.E_FLAT_MAJOR_C_MINOR,
    "E_MAJOR_D_FLAT_MINOR": types.Scale.E_MAJOR_D_FLAT_MINOR,
    "F_MAJOR_D_MINOR": types.Scale.F_MAJOR_D_MINOR,
    "G_FLAT_MAJOR_E_FLAT_MINOR": types.Scale.G_FLAT_MAJOR_E_FLAT_MINOR,
    "G_MAJOR_E_MINOR": types.Scale.G_MAJOR_E_MINOR,
    "A_FLAT_MAJOR_F_MINOR": types.Scale.A_FLAT_MAJOR_F_MINOR,
    "A_MAJOR_G_FLAT_MINOR": types.Scale.A_MAJOR_G_FLAT_MINOR,
    "B_FLAT_MAJOR_G_MINOR": types.Scale.B_FLAT_MAJOR_G_MINOR,
    "B_MAJOR_A_FLAT_MINOR": types.Scale.B_MAJOR_A_FLAT_MINOR,
}

DEFAULT_DURATION_SECONDS = 30


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_music(
        prompts: list[dict],
        bpm: int | None = None,
        temperature: float = 1.0,
        scale: str | None = None,
        duration_seconds: int | None = None,
        ctx: Context = None,
    ) -> CallToolResult:
        """Generate instrumental music from weighted text prompts using Google's Lyria model.

        Each prompt has a 'text' describing genre/instrument/mood and a 'weight'
        for emphasis. The server manages the streaming session internally.
        """
        app: AppContext = ctx.request_context.lifespan_context

        if not prompts:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="[validation] At least one prompt is required.",
                )],
                isError=True,
            )

        weighted_prompts = [
            types.WeightedPrompt(text=p["text"], weight=p["weight"])
            for p in prompts
        ]

        music_config_kwargs: dict = {
            "temperature": temperature,
        }
        if bpm is not None:
            music_config_kwargs["bpm"] = bpm
        if scale and scale in SCALE_MAP:
            music_config_kwargs["scale"] = SCALE_MAP[scale]

        target_duration = duration_seconds or DEFAULT_DURATION_SECONDS
        audio_data = bytearray()

        try:
            async with app.client.aio.live.music.connect(
                model="models/lyria-realtime-exp"
            ) as session:
                await session.set_weighted_prompts(prompts=weighted_prompts)
                await session.set_music_generation_config(
                    config=types.LiveMusicGenerationConfig(
                        **music_config_kwargs
                    )
                )
                await session.play()

                start_time = time.monotonic()
                async for message in session.receive():
                    elapsed = time.monotonic() - start_time
                    if elapsed >= target_duration:
                        break

                    await ctx.report_progress(
                        progress=elapsed,
                        total=float(target_duration),
                    )

                    if (
                        hasattr(message, "server_content")
                        and message.server_content
                        and message.server_content.audio_chunks
                    ):
                        audio_data.extend(
                            message.server_content.audio_chunks[0].data
                        )

        except Exception as e:
            if audio_data:
                # Partial audio collected before error — return what we have
                pass
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=handle_gemini_error(e),
                    )],
                    isError=True,
                )

        if not audio_data:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="[error] No audio data received from music generation.",
                )],
                isError=True,
            )

        wav_data = pcm_to_wav_music(bytes(audio_data))

        if app.config.output_dir:
            filename = generate_filename("music", "wav")
            path = save_media_file(wav_data, app.config.output_dir, filename)
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Music generated and saved to: {path}",
                )]
            )

        return CallToolResult(
            content=[
                AudioContent(
                    type="audio",
                    data=encode_base64(wav_data),
                    mimeType="audio/wav",
                )
            ]
        )
