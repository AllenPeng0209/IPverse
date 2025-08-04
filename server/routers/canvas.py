from fastapi import APIRouter, Request
#from routers.agent import chat
from services.chat_service import handle_chat
from services.db_adapter import db_adapter
import asyncio
import json
import httpx
import os

router = APIRouter(prefix="/api/canvas")

@router.get("/list")
async def list_canvases():
    return await db_adapter.list_canvases()

@router.post("/create")
async def create_canvas(request: Request):
    data = await request.json()
    id = data.get('canvas_id')
    name = data.get('name')

    asyncio.create_task(handle_chat(data))
    await db_adapter.create_canvas(id, name)
    return {"id": id }

@router.get("/{id}")
async def get_canvas(id: str):
    return await db_adapter.get_canvas_data(id)

@router.post("/{id}/save")
async def save_canvas(id: str, request: Request):
    payload = await request.json()
    data_str = json.dumps(payload['data'])
    await db_adapter.save_canvas_data(id, data_str, payload['thumbnail'])
    return {"id": id }

@router.post("/{id}/rename")
async def rename_canvas(id: str, request: Request):
    data = await request.json()
    name = data.get('name')
    await db_adapter.rename_canvas(id, name)
    return {"id": id }

@router.delete("/{id}/delete")
async def delete_canvas(id: str):
    await db_adapter.delete_canvas(id)
    return {"id": id }

@router.post("/{id}/cleanup")
async def cleanup_canvas_images(id: str):
    """清理畫布中無效的圖片元素"""
    
    # 獲取畫布數據
    canvas_data = await db_adapter.get_canvas_data(id)
    if not canvas_data or 'data' not in canvas_data:
        return {"message": "Canvas not found", "removed_count": 0}
    
    data = canvas_data['data']
    if not isinstance(data, dict) or 'elements' not in data:
        return {"message": "No elements to cleanup", "removed_count": 0}
    
    original_count = len(data['elements'])
    invalid_elements = []
    valid_elements = []
    
    # 檢查每個圖片元素的有效性
    async with httpx.AsyncClient() as client:
        for element in data['elements']:
            if element.get('type') == 'image':
                file_id = element.get('fileId')
                if file_id:
                    # 檢查圖片文件是否可訪問
                    try:
                        from services.config_service import DEFAULT_PORT
                        is_cloud_deployment = os.environ.get('CLOUD_DEPLOYMENT', 'false').lower() == 'true'
                        if is_cloud_deployment:
                            backend_url = 'https://jaaz-backend-337074826438.asia-northeast1.run.app'
                        else:
                            backend_url = f'http://localhost:{DEFAULT_PORT}'
                        
                        file_url = f"{backend_url}/api/file/{file_id}"
                        response = await client.head(file_url, timeout=3.0)
                        
                        if response.status_code == 200:
                            valid_elements.append(element)
                            print(f"✅ Valid image: {file_id}")
                        else:
                            invalid_elements.append(element)
                            print(f"❌ Invalid image: {file_id} (HTTP {response.status_code})")
                    except Exception as e:
                        print(f"❌ Error checking image {file_id}: {e}")
                        invalid_elements.append(element)
                else:
                    invalid_elements.append(element)
                    print(f"❌ Image element without fileId")
            else:
                # 非圖片元素，保留
                valid_elements.append(element)
    
    # 更新畫布數據
    data['elements'] = valid_elements
    
    # 清理對應的 files 數據
    if 'files' in data:
        valid_file_ids = set()
        for element in valid_elements:
            if element.get('type') == 'image' and element.get('fileId'):
                valid_file_ids.add(element['fileId'])
        
        # 只保留有效的文件
        data['files'] = {
            file_id: file_data 
            for file_id, file_data in data['files'].items() 
            if file_id in valid_file_ids
        }
    
    # 保存更新後的畫布數據
    data_str = json.dumps(data)
    await db_adapter.save_canvas_data(id, data_str, canvas_data.get('thumbnail'))
    
    removed_count = len(invalid_elements)
    
    print(f"🧹 Canvas cleanup complete: removed {removed_count} invalid elements")
    
    return {
        "message": f"Cleanup complete",
        "original_count": original_count,
        "removed_count": removed_count,
        "remaining_count": len(valid_elements),
        "invalid_elements": [{"type": elem.get("type"), "fileId": elem.get("fileId")} for elem in invalid_elements]
    }