import { Model } from '@/types/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://jaaz-backend-337074826438.asia-northeast1.run.app'

export interface ModelInfo {
  provider: string
  model: string
  url: string
  type?: 'text' | 'image' | 'video'
}

export interface ToolInfo {
  id: string
  name: string
  description: string
  provider?: string
  type?: string
  display_name?: string
  parameters?: any
}

export const getPlatformModels = async (): Promise<Model[]> => {
  const response = await fetch(`${API_BASE_URL}/api/list_models`)
  const data = await response.json()
  // The backend seems to return { models: [...] }, so we extract it.
  return data.models || data
}

export const getPlatformTools = async (): Promise<ToolInfo[]> => {
  const response = await fetch(`${API_BASE_URL}/api/list_tools`)
  const data = await response.json()
  return Array.isArray(data) ? data : []
}
