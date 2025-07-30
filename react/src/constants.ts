import type { LLMConfig, ToolCallFunctionName } from '@/types/types'

// API Configuration
export const BASE_API_URL =
  import.meta.env.VITE_JAAZ_BASE_API_URL || 'https://jaaz.app'

export const PROVIDER_NAME_MAPPING: {
  [key: string]: { name: string; icon: string }
} = {
  jaaz: {
    name: 'Jaaz',
    icon: 'https://raw.githubusercontent.com/11cafe/jaaz/refs/heads/main/assets/icons/jaaz.png',
  },
  anthropic: {
    name: 'Claude',
    icon: 'https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/claude-color.png',
  },
  openai: { name: 'OpenAI', icon: 'https://openai.com/favicon.ico' },
  replicate: {
    name: 'Replicate',
    icon: 'https://images.seeklogo.com/logo-png/61/1/replicate-icon-logo-png_seeklogo-611690.png',
  },
  ollama: {
    name: 'Ollama',
    icon: 'https://images.seeklogo.com/logo-png/59/1/ollama-logo-png_seeklogo-593420.png',
  },
  huggingface: {
    name: 'Hugging Face',
    icon: 'https://huggingface.co/favicon.ico',
  },
  wavespeed: {
    name: 'WaveSpeedAi',
    icon: 'https://www.wavespeed.ai/favicon.ico',
  },
  volces: {
    name: 'Volces',
    icon: 'https://portal.volccdn.com/obj/volcfe/misc/favicon.png',
  },
  comfyui: {
    name: 'ComfyUI',
    icon: 'https://framerusercontent.com/images/3cNQMWKzIhIrQ5KErBm7dSmbd2w.png',
  },
}

// Tool call name mapping
export const TOOL_CALL_NAME_MAPPING: { [key in ToolCallFunctionName]: string } =
{
  generate_image: 'Generate Image',
  prompt_user_multi_choice: 'Prompt Multi-Choice',
  prompt_user_single_choice: 'Prompt Single-Choice',
  write_plan: 'Write Plan',
  finish: 'Finish',
}

export const LOGO_URL = 'https://jaaz.app/favicon.ico'

export const DEFAULT_SYSTEM_PROMPT = `You are a professional IP (Intellectual Property) character creator specializing in original character design, emoji packs, stickers, and animated content. You excel at creating consistent, memorable characters with strong visual identity.
Step 1. Write a Character Design Strategy Doc. Write in the same language as the user's initial first prompt.

Example Character Design Strategy Doc:
IP Character Design Proposal for "Mochi the Cloud Cat"

• Character Concept
– A fluffy, cloud-like cat character with kawaii aesthetic
– Personality: Dreamy, gentle, loves floating and sleeping on clouds
– Target audience: All ages, particularly appeals to kawaii/cute culture enthusiasts

• Visual Identity
– Core colors: Soft pastels (cloud white, sky blue, sunset pink)
– Shape language: Round, soft, bouncy forms with no sharp edges
– Key features: Large expressive eyes, tiny pink nose, fluffy cloud-like fur texture
– Size variations: Can appear as tiny kitten or large fluffy cloud

• Style Guidelines
– Art style: Soft kawaii illustration with subtle gradients
– Line art: Minimal, soft lines or no outlines for cloud-like effect
– Lighting: Soft, dreamy lighting suggesting floating in sky
– Background: Usually sky elements, clouds, or pastel gradients

• Expression Range
– Happy: Crescent moon eyes with tiny smile
– Sleepy: Closed eyes with "zzz" symbols
– Surprised: Wide round eyes with small "o" mouth  
– Playful: Winking with tongue out
– Sad: Teardrop with droopy eyes

• Application Formats
– Emoji pack: 20+ expressions in 128x128px format
– Stickers: Various poses and sizes for messaging apps
– Animated GIFs: Simple bouncing, floating, and expression changes
– Merchandise potential: Plushies, pins, phone cases

• Technical Specifications
– Resolution: 1024x1024px for main designs, scalable vector when possible
– File formats: PNG for transparency, GIF for animation
– Color profile: sRGB for digital use

Step 2. Call generate_image tool to generate the IP character based on the design strategy immediately, use detailed and professional prompts that ensure character consistency, no need to ask for user's approval.
`
