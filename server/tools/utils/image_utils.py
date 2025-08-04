import os
import traceback
from PIL import Image, PngImagePlugin
from io import BytesIO
import base64
import json
from typing import Any, Optional, Tuple
from nanoid import generate
from utils.http_client import HttpClient
from services.config_service import FILES_DIR


def generate_image_id() -> str:
    """Generate unique image ID"""
    return generate(size=10)


async def get_image_info_and_save(
    url: str,
    file_path_without_extension: str,
    is_b64: bool = False,
    metadata: Optional[dict[str, Any]] = None
) -> Tuple[str, int, int, str]:
    """
    Download image from URL or decode base64, convert to PNG and save with metadata

    Args:
        url: Image URL or base64 string
        file_path_without_extension: File path without extension
        is_b64: Whether the url is a base64 string
        metadata: Optional metadata to be saved in PNG info

    Returns:
        tuple[str, int, int, str]: (mime_type, width, height, extension) - always PNG
    """
    try:
        if is_b64:
            image_data = base64.b64decode(url)
        else:
            # Fetch the image asynchronously
            async with HttpClient.create_aiohttp() as session:
                async with session.get(url) as response:
                    # Read the image content as bytes
                    image_data = await response.read()

        # Open image to get info
        image = Image.open(BytesIO(image_data))
        width, height = image.size
        
        # Store original format for debugging
        original_format = image.format or 'Unknown'
        print(f"Converting {original_format} image to PNG: {width}x{height}")

        # Handle different color modes properly for PNG conversion
        if image.mode == 'P':
            # Palette mode - convert to RGBA to preserve potential transparency
            if 'transparency' in image.info:
                image = image.convert('RGBA')
            else:
                image = image.convert('RGB')
        elif image.mode == 'LA':
            # Grayscale with alpha - convert to RGBA
            image = image.convert('RGBA')
        elif image.mode == 'L':
            # Grayscale - can stay as L or convert to RGB
            # PNG supports grayscale, so we can keep it
            pass
        elif image.mode == 'CMYK':
            # CMYK mode - convert to RGB
            image = image.convert('RGB')
        elif image.mode in ('RGB', 'RGBA'):
            # Already compatible with PNG
            pass
        else:
            # For any other modes, convert to RGB as a safe fallback
            print(f"Warning: Unusual color mode {image.mode}, converting to RGB")
            image = image.convert('RGB')

        # Unified format: always PNG
        extension = 'png'
        mime_type = 'image/png'

        # Prepare PNG info for metadata
        pnginfo = PngImagePlugin.PngInfo()
        
        # Add original format info
        pnginfo.add_text("original_format", original_format)
        
        if metadata:
            for key, value in metadata.items():
                try:
                    # Handle different value types
                    if isinstance(value, (dict, list)):
                        # Serialize complex types as JSON
                        text_value = json.dumps(value, ensure_ascii=False)
                    elif value is None:
                        text_value = "null"
                    else:
                        # Convert to string
                        text_value = str(value)
                    
                    pnginfo.add_text(str(key), text_value)
                except Exception as e:
                    print(f"Warning: Failed to add metadata key '{key}': {e}")
                    traceback.print_stack()

        # Save as PNG with metadata
        file_path = f"{file_path_without_extension}.{extension}"
        
        # Save with optimizations and metadata
        if metadata or original_format != 'PNG':
            image.save(file_path, format='PNG', optimize=True, pnginfo=pnginfo)
        else:
            image.save(file_path, format='PNG', optimize=True)
        
        print(f"Successfully saved as PNG: {file_path}")
        return mime_type, width, height, extension

    except Exception as e:
        print(f"Error processing image: {e}")
        raise e


# Canvas-related utilities have been moved to tools/image_generation/image_canvas_utils.py


# Canvas element generation moved to tools/image_generation/image_canvas_utils.py


# Canvas saving functionality moved to tools/image_generation/image_canvas_utils.py


# Image generation orchestration moved to tools/image_generation/image_generation_core.py
# Notification functions moved to tools/image_generation/image_canvas_utils.py


async def process_input_image(input_image: str | None) -> str | None:
    """
    Process input image and convert to base64 format

    Args:
        input_image: Image file path or filename

    Returns:
        Base64 encoded image with data URL, or None if no image
    """
    if not input_image:
        return None

    try:
        # First try local file
        full_path = os.path.join(FILES_DIR, input_image)
        image = None
        
        if os.path.exists(full_path):
            # Load from local file
            print(f"📁 Loading image from local file: {full_path}")
            image = Image.open(full_path)
        else:
            # Try to load from backend URL (for images stored in Supabase but with local fallback)
            print(f"🌐 Local file not found, trying to load from backend URL: {input_image}")
            
            # Construct the backend URL
            import os as env_os
            is_cloud_deployment = env_os.environ.get('CLOUD_DEPLOYMENT', 'false').lower() == 'true'
            if is_cloud_deployment:
                backend_url = 'https://jaaz-backend-337074826438.asia-northeast1.run.app'
            else:
                backend_url = env_os.environ.get('BACKEND_URL', 'http://localhost:8080')
            
            image_url = f'{backend_url}/api/file/{input_image}'
            print(f"🔗 Fetching image from: {image_url}")
            
            # Use aiohttp to fetch the image
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image = Image.open(BytesIO(image_data))
                        print(f"✅ Successfully loaded image from URL")
                    else:
                        print(f"❌ Failed to fetch image from URL, status: {response.status}")
                        return None

        if not image:
            print(f"❌ Could not load image: {input_image}")
            return None

        # Get file extension and determine MIME type
        ext = os.path.splitext(input_image)[1].lower()
        mime_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }
        mime_type = mime_type_map.get(ext, 'image/jpeg')

        # Convert to base64
        with BytesIO() as output:
            format_name = str(mime_type.split('/')[1]).upper()
            if format_name == 'JPEG':
                # Convert RGBA to RGB for JPEG
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
            
            image.save(output, format=format_name)
            compressed_data = output.getvalue()
            b64_data = base64.b64encode(compressed_data).decode('utf-8')

        data_url = f"data:{mime_type};base64,{b64_data}"
        print(f"🖼️ Successfully converted image to base64 data URL")
        return data_url

    except Exception as e:
        print(f"❌ Error processing image {input_image}: {e}")
        import traceback
        traceback.print_exc()
        return None
