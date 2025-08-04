from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from common import DEFAULT_PORT
from tools.utils.image_canvas_utils import generate_file_id
from services.config_service import FILES_DIR
from services.supabase_storage_service import supabase_storage

from PIL import Image
from io import BytesIO
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
import httpx
import aiofiles
from mimetypes import guess_type
from utils.http_client import HttpClient

router = APIRouter(prefix="/api")
os.makedirs(FILES_DIR, exist_ok=True)

# 上传图片接口，支持表单提交
@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...), max_size_mb: float = 3.0):
    print('🦄upload_image file', file.filename)
    # 生成文件 ID 和文件名
    file_id = generate_file_id()
    filename = file.filename or ''

    # Read the file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")
    original_size_mb = len(content) / (1024 * 1024)  # Convert to MB

    # Open the image from bytes to get its dimensions
    with Image.open(BytesIO(content)) as img:
        width, height = img.size
        
        # Check if compression is needed
        if original_size_mb > max_size_mb:
            print(f'🦄 Image size ({original_size_mb:.2f}MB) exceeds limit ({max_size_mb}MB), compressing...')
            
            # Convert to RGB if necessary (for JPEG compression)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compress the image
            compressed_content = compress_image(img, max_size_mb)
            
            # Save compressed image using Image.save
            extension = 'jpg'  # Force JPEG for compressed images
            file_path = os.path.join(FILES_DIR, f'{file_id}.{extension}')
            
            # Create new image from compressed content and save
            with Image.open(BytesIO(compressed_content)) as compressed_img:
                width, height = compressed_img.size
                await run_in_threadpool(compressed_img.save, file_path, format='JPEG', quality=95, optimize=True)
                # compressed_img.save(file_path, format='JPEG', quality=95, optimize=True)
            
            final_size_mb = len(compressed_content) / (1024 * 1024)
            print(f'🦄 Compressed from {original_size_mb:.2f}MB to {final_size_mb:.2f}MB')
        else:
            # Determine the file extension from original file
            mime_type, _ = guess_type(filename)
            if mime_type and mime_type.startswith('image/'):
                extension = mime_type.split('/')[-1]
                # Handle common image format mappings
                if extension == 'jpeg':
                    extension = 'jpg'
            else:
                extension = 'jpg'  # Default to jpg for unknown types
            
            # Save original image using Image.save
            file_path = os.path.join(FILES_DIR, f'{file_id}.{extension}')
            
            # Determine save format based on extension
            save_format = 'JPEG' if extension.lower() in ['jpg', 'jpeg'] else extension.upper()
            if save_format == 'JPEG':
                img = img.convert('RGB')
            
            # img.save(file_path, format=save_format)
            await run_in_threadpool(img.save, file_path, format=save_format)

    # 確定後端 URL（雲端部署或本地開發）
    is_cloud_deployment = os.environ.get('CLOUD_DEPLOYMENT', 'false').lower() == 'true'
    if is_cloud_deployment:
        # 雲端部署使用 Cloud Run URL
        backend_url = 'https://jaaz-backend-337074826438.asia-northeast1.run.app'
    else:
        # 本地開發
        backend_url = os.environ.get('BACKEND_URL', f'http://localhost:{DEFAULT_PORT}')
    
    # 默認使用後端文件服務 URL
    final_url = f'{backend_url}/api/file/{file_id}.{extension}'
    
    # 嘗試上傳到 Supabase Storage（如果已配置）
    if supabase_storage.initialized:
        try:
            # Storage path in Supabase
            storage_path = f"uploads/{file_id}.{extension}"
            
            # Upload to Supabase Storage
            public_url = await supabase_storage.upload_file(file_path, storage_path)
            
            # Use Supabase URL (優先使用 Supabase 的公共 URL)
            final_url = public_url
            
            print(f"✅ Image uploaded to Supabase Storage: {public_url}")
            
            # Optionally remove local file to save space
            try:
                os.remove(file_path)
                print(f"🗑️ Removed local file: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove local file: {e}")
                
        except Exception as e:
            print(f"❌ Failed to upload to Supabase Storage: {e}")
            # Fallback 已經在上面設置好了
            print(f"📁 Using fallback URL: {final_url}")

    # 返回文件信息
    print('🦄upload_image file_path', file_path)
    print('🦄upload_image final_url', final_url)
    return {
        'file_id': f'{file_id}.{extension}',
        'url': final_url,
        'width': width,
        'height': height,
    }


def compress_image(img: Image.Image, max_size_mb: float) -> bytes:
    """
    Compress an image to be under the specified size limit.
    """
    # Start with high quality
    quality = 95
    
    while quality > 10:
        # Save to bytes buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        # Check size
        size_mb = len(buffer.getvalue()) / (1024 * 1024)
        
        if size_mb <= max_size_mb:
            return buffer.getvalue()
        
        # Reduce quality for next iteration
        quality -= 10
    
    # If still too large, try reducing dimensions
    original_width, original_height = img.size
    scale_factor = 0.8
    
    while scale_factor > 0.3:
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Try with moderate quality
        buffer = BytesIO()
        resized_img.save(buffer, format='JPEG', quality=70, optimize=True)
        
        size_mb = len(buffer.getvalue()) / (1024 * 1024)
        
        if size_mb <= max_size_mb:
            return buffer.getvalue()
        
        scale_factor -= 0.1
    
    # Last resort: very low quality
    buffer = BytesIO()
    resized_img.save(buffer, format='JPEG', quality=30, optimize=True)
    return buffer.getvalue()


# 文件下载接口
@router.get("/file/{file_id}")
async def get_file(file_id: str):
    from fastapi.responses import RedirectResponse
    
    file_path = os.path.join(FILES_DIR, f'{file_id}')
    print('🦄get_file file_path', file_path)
    
    # 首先嘗試從本地文件系統提供文件
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # 如果本地文件不存在，嘗試從 Supabase Storage 查找
    if supabase_storage.initialized:
        try:
            # 先嘗試常見的直接路徑
            common_paths = [
                f"uploads/{file_id}",    # 聊天上傳路徑
            ]
            
            for storage_path in common_paths:
                public_url = f"{supabase_storage.supabase_url}/storage/v1/object/public/{supabase_storage.bucket_name}/{storage_path}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.head(public_url, timeout=3.0)
                    if response.status_code == 200:
                        print(f"🔗 Found at {storage_path}, redirecting to: {public_url}")
                        return RedirectResponse(url=public_url, status_code=302)
                        
        except Exception as e:
            print(f"❌ Error checking common paths: {e}")
            
        # 如果直接路徑沒找到，嘗試通過模式匹配查找 canvas 路徑
        try:
            # 我們知道 canvas 文件的格式是: canvas/{canvas_id}/{filename}
            # 動態獲取所有 canvas ID 來查找文件
            
            from services.db_adapter import db_adapter
            
            # 獲取所有 canvas ID
            try:
                canvases = await db_adapter.list_canvases()
                canvas_ids = [canvas.get('id') for canvas in canvases if canvas.get('id')]
                print(f"🔍 Found {len(canvas_ids)} canvas IDs to search")
            except Exception as e:
                print(f"⚠️ Could not get canvas IDs from database: {e}")
                # 回退到硬編碼的已知路徑
                canvas_ids = [
                    "Tu9xMOoLtND6s_gZyiMhi",  # 當前用戶的canvas
                    "qiOuoR0GhB_SUAfiQ5evF",  # 已知存在的路徑
                    "H7L9rSfAami0LK-MYIGO1",  # 已知存在的路徑  
                    "et1KGstRGHyPnMlXdxssK",  # 已知存在的路徑
                ]
            
            async with httpx.AsyncClient() as client:
                for canvas_id in canvas_ids:
                    test_url = f"{supabase_storage.supabase_url}/storage/v1/object/public/{supabase_storage.bucket_name}/canvas/{canvas_id}/{file_id}"
                    
                    try:
                        response = await client.head(test_url, timeout=3.0)
                        if response.status_code == 200:
                            print(f"🔗 Found file at: canvas/{canvas_id}/{file_id} -> {test_url}")
                            return RedirectResponse(url=test_url, status_code=302)
                    except Exception as e:
                        # 不打印每個失敗的嘗試，避免日誌過多
                        continue
                        
                print(f"🔍 File {file_id} not found in any canvas paths (checked {len(canvas_ids)} canvases)")
                    
        except Exception as e:
            print(f"❌ Error searching canvas paths: {e}")
    
    # 如果都找不到，返回 404
    raise HTTPException(status_code=404, detail="File not found")


@router.post("/comfyui/object_info")
async def get_object_info(data: dict):
    url = data.get('url', '')
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        timeout = httpx.Timeout(10.0)
        async with HttpClient.create(timeout=timeout) as client:
            response = await client.get(f"{url}/api/object_info")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=f"ComfyUI server returned status {response.status_code}")
    except Exception as e:
        if "ConnectError" in str(type(e)) or "timeout" in str(e).lower():
            print(f"ComfyUI connection error: {str(e)}")
            raise HTTPException(
                status_code=503, detail="ComfyUI server is not available. Please make sure ComfyUI is running.")
        print(f"Unexpected error connecting to ComfyUI: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to connect to ComfyUI: {str(e)}")


# 添加 /upload 路由作為 /upload_image 的別名，以兼容前端
@router.post("/upload")
async def upload(file: UploadFile = File(...), max_size_mb: float = 3.0):
    """上传图片接口的别名，兼容前端 /api/upload 请求"""
    return await upload_image(file, max_size_mb)
