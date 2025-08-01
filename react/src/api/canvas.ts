import { CanvasData, Message, Session } from '@/types/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://jaaz-backend-337074826438.asia-northeast1.run.app'

export type ListCanvasesResponse = {
  id: string
  name: string
  description?: string
  thumbnail?: string
  created_at: string
}

export async function listCanvases(): Promise<ListCanvasesResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/list`)
  const data = await response.json()
  // Convert the response to match ListCanvasesResponse format
  return data.map((canvas: any) => ({
    id: canvas.id,
    name: canvas.name,
    description: canvas.description,
    thumbnail: canvas.thumbnail,
    created_at: canvas.created_at || new Date().toISOString()
  }))
}

export async function createCanvas(data: {
  name: string
  canvas_id: string
  messages: Message[]
  session_id: string
  text_model: {
    provider: string
    model: string
    url: string
  }
  tool_list: any[] // ToolInfo[] // This type was removed, so we use 'any' for now

  system_prompt: string
}): Promise<{ id: string }> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return await response.json()
}

export async function getCanvas(
  id: string
): Promise<{ data: CanvasData; name: string; sessions: Session[] }> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/${id}`)
  return await response.json()
}

export async function saveCanvas(
  id: string,
  payload: {
    data: CanvasData
    thumbnail: string
  }
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/${id}/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return await response.json()
}

export async function renameCanvas(id: string, name: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/${id}/rename`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
  return await response.json()
}

export async function deleteCanvas(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/canvas/${id}/delete`, {
    method: 'DELETE',
  })
  return await response.json()
}
