from fastapi import APIRouter, Request
#from routers.agent import chat
from services.chat_service import handle_chat
from services.db_adapter import db_adapter
import asyncio
import json

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