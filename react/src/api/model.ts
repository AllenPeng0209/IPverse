import { Model } from '@/types/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const getPlatformModels = async (): Promise<Model[]> => {
  const response = await fetch(`${API_BASE_URL}/api/list_models`)
  const data = await response.json()
  // The backend seems to return { models: [...] }, so we extract it.
  return data.models || data
}
