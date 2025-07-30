from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId  # type: ignore
from langchain_core.runnables import RunnableConfig
from tools.utils.image_generation_core import generate_image_with_provider


class GenerateImageByIdeogram3InputSchema(BaseModel):
    prompt: str = Field(
        description="Required. The prompt for IP character creation. Be specific about character design, style, and visual elements. Perfect for creating new original characters from scratch."
    )
    aspect_ratio: str = Field(
        description="Required. Aspect ratio of the image, only these values are allowed: 1:1, 16:9, 4:3, 3:4, 9:16. For IP characters: use 1:1 for emoji/stickers, 3:4 for character sheets, 16:9 for promotional art."
    )
    tool_call_id: Annotated[str, InjectedToolCallId]


@tool("generate_image_by_ideogram3_bal_jaaz",
      description="Create original IP characters using Ideogram 3 balanced model. Excellent for generating new character concepts from text descriptions. Perfect for initial character design and brainstorming. This model creates fresh designs without input images.",
      args_schema=GenerateImageByIdeogram3InputSchema)
async def generate_image_by_ideogram3_bal_jaaz(
    prompt: str,
    aspect_ratio: str,
    config: RunnableConfig,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    ctx = config.get('configurable', {})
    canvas_id = ctx.get('canvas_id', '')
    session_id = ctx.get('session_id', '')

    return await generate_image_with_provider(
        canvas_id=canvas_id,
        session_id=session_id,
        provider='jaaz',
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        model="ideogram-ai/ideogram-v3-balanced",
        input_images=None,
    )


# Export the tool for easy import
__all__ = ["generate_image_by_ideogram3_bal_jaaz"]
