from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId  # type: ignore
from langchain_core.runnables import RunnableConfig
from tools.utils.image_generation_core import generate_image_with_provider


class GenerateImageByGptImage1InputSchema(BaseModel):
    prompt: str = Field(
        description="Required. The prompt for IP character creation or editing. Be detailed about character features, expressions, poses, and visual style to maintain consistency across your IP character series."
    )
    aspect_ratio: str = Field(
        description="Required. Aspect ratio of the image, only these values are allowed: 1:1, 16:9, 4:3, 3:4, 9:16. For IP characters: use 1:1 for emoji/stickers, 3:4 for character portraits, 16:9 for animated scenes"
    )
    input_images: list[str] | None = Field(
        default=None,
        description="Optional; One or multiple IP character reference images. Pass a list of image_id here, e.g. ['im_jurheut7.png', 'im_hfuiut78.png']. Perfect for: Maintaining character consistency across expressions, Creating character variations and poses, Generating emoji packs with consistent style, Character evolution and redesign, Style transfer for character branding."
    )
    tool_call_id: Annotated[str, InjectedToolCallId]


@tool("generate_image_by_gpt_image_1_jaaz",
      description="Generate IP characters, emoji packs, and stickers using GPT image model. Perfect for creating consistent character designs across multiple expressions and poses. Use this tool when you need multiple input images as reference for character consistency. Ideal for emoji packs, character variations, and brand mascot creation.",
      args_schema=GenerateImageByGptImage1InputSchema)
async def generate_image_by_gpt_image_1_jaaz(
    prompt: str,
    aspect_ratio: str,
    config: RunnableConfig,
    tool_call_id: Annotated[str, InjectedToolCallId],
    input_images: list[str] | None = None,
) -> str:
    ctx = config.get('configurable', {})
    canvas_id = ctx.get('canvas_id', '')
    session_id = ctx.get('session_id', '')
    return await generate_image_with_provider(
        canvas_id=canvas_id,
        session_id=session_id,
        provider='jaaz',
        model='openai/gpt-image-1',
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        input_images=input_images,
    )


# Export the tool for easy import
__all__ = ["generate_image_by_gpt_image_1_jaaz"]
