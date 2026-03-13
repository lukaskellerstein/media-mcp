from __future__ import annotations

from typing import Literal

from google.genai import types
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import AudioContent, CallToolResult, TextContent

from media_mcp.server import AppContext, handle_gemini_error
from media_mcp.utils.audio import pcm_to_wav_speech
from media_mcp.utils.media import (
    encode_base64,
    generate_filename,
    save_media_file,
)

MODEL_MAP = {
    "flash-tts": "gemini-2.5-flash-preview-tts",
    "pro-tts": "gemini-2.5-pro-preview-tts",
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_speech(
        text: str,
        model: Literal["flash-tts", "pro-tts"] = "flash-tts",
        voice_name: str | None = None,
        multi_speaker: bool = False,
        speakers: list[dict] | None = None,
        style_instructions: str | None = None,
        ctx: Context = None,
    ) -> CallToolResult:
        """Generate speech audio from text using Gemini TTS models.

        Supports single-speaker and multi-speaker modes with voice selection
        and natural language style control.
        """
        app: AppContext = ctx.request_context.lifespan_context

        if not text.strip():
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="[validation] Text must not be empty.",
                )],
                isError=True,
            )

        gemini_model = MODEL_MAP[model]

        if multi_speaker and speakers:
            speaker_configs = [
                types.SpeakerVoiceConfig(
                    speaker=s["name"],
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=s["voice_name"]
                        )
                    ),
                )
                for s in speakers
            ]
            speech_config = types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=speaker_configs
                )
            )
        else:
            voice_cfg = None
            if voice_name:
                voice_cfg = types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            speech_config = types.SpeechConfig(voice_config=voice_cfg)

        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        )

        content_text = text
        if style_instructions:
            content_text = f"{style_instructions}: {text}"

        try:
            response = app.client.models.generate_content(
                model=gemini_model,
                contents=content_text,
                config=config,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=handle_gemini_error(e))],
                isError=True,
            )

        pcm_data = response.candidates[0].content.parts[0].inline_data.data
        wav_data = pcm_to_wav_speech(pcm_data)

        result_content: list = [
            AudioContent(
                type="audio",
                data=encode_base64(wav_data),
                mimeType="audio/wav",
            )
        ]

        if app.config.output_dir:
            filename = generate_filename("speech", "wav")
            path = save_media_file(wav_data, app.config.output_dir, filename)
            result_content.append(
                TextContent(type="text", text=f"Saved to: {path}")
            )

        return CallToolResult(content=result_content)
