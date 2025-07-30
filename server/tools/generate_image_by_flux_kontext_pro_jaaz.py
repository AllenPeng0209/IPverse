from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId  # type: ignore
from langchain_core.runnables import RunnableConfig
from tools.utils.image_generation_core import generate_image_with_provider


class GenerateImageByFluxKontextProInputSchema(BaseModel):
    prompt: str = Field(
        description="Required. The prompt for IP character creation or editing. Describe character features, expressions, or modifications needed. Great for character refinement and style adjustments."
    )
    aspect_ratio: str = Field(
        description="Required. Aspect ratio of the image, only these values are allowed: 1:1, 16:9, 4:3, 3:4, 9:16. For IP characters: use 1:1 for emoji/stickers, 3:4 for character portraits, 16:9 for scenes"
    )
    input_images: list[str]| None = Field(
        default=None,
        description="Optional; Single IP character reference image. Only one image is allowed, e.g. ['im_jurheut7.png']. Perfect for: Character pose adjustments, Expression modifications, Style refinement, Character outfit changes, Background removal/replacement for character focus."
    )
    tool_call_id: Annotated[str, InjectedToolCallId]


@tool("generate_image_by_flux_kontext_pro_jaaz",
      description="Generate and edit IP characters using Flux Kontext Pro model. Excellent for character refinement, pose adjustments, expression changes, and style modifications. Perfect for polishing your IP character designs and creating variations. Only one input image is allowed.",
      args_schema=GenerateImageByFluxKontextProInputSchema)
async def generate_image_by_flux_kontext_pro_jaaz(
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
        model='black-forest-labs/flux-kontext-pro',
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        input_images=input_images,
    )

# Export the tool for easy import
__all__ = ["generate_image_by_flux_kontext_pro_jaaz"]
