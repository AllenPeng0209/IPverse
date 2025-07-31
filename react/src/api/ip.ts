import { BASE_API_URL } from '../constants'

export interface IPCategory {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
}

export interface IP {
  id: number
  name: string
  description: string
  image_url: string
  heat_score: number
  view_count: number
  like_count: number
  tags: string[]
  category_name?: string
  category_id?: number
  created_at?: string
  updated_at?: string
}

export interface InteractionRequest {
  interaction_type: 'view' | 'like' | 'share' | 'comment'
  user_identifier?: string
}

export interface APIResponse<T> {
  success: boolean
  data: T
  count?: number
  message?: string
}

// 获取热度排行榜
export const getTopIPs = async (limit: number = 10): Promise<IP[]> => {
  const response = await fetch(`${BASE_API_URL}/api/ip/top?limit=${limit}`)
  if (!response.ok) {
    throw new Error('Failed to fetch top IPs')
  }
  const result: APIResponse<IP[]> = await response.json()
  return result.data
}

// 获取IP详情
export const getIPDetails = async (ipId: number): Promise<IP> => {
  const response = await fetch(`${BASE_API_URL}/api/ip/${ipId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch IP details')
  }
  const result: APIResponse<IP> = await response.json()
  return result.data
}

// 记录IP交互
export const recordIPInteraction = async (
  ipId: number,
  interaction: InteractionRequest
): Promise<void> => {
  await fetch(`${BASE_API_URL}/api/ip/${ipId}/interaction`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(interaction),
  })
}

// 获取IP分类
export const getIPCategories = async (): Promise<IPCategory[]> => {
  const response = await fetch(`${BASE_API_URL}/api/ip/categories`)
  if (!response.ok) {
    throw new Error('Failed to fetch IP categories')
  }
  const result: APIResponse<IPCategory[]> = await response.json()
  return result.data
}

// 搜索IP
export const searchIPs = async (
  query?: string,
  categoryId?: number,
  limit: number = 20
): Promise<IP[]> => {
  const params = new URLSearchParams()
  if (query) params.append('q', query)
  if (categoryId) params.append('category_id', categoryId.toString())
  params.append('limit', limit.toString())

  const response = await fetch(`${BASE_API_URL}/api/ip/search?${params}`)
  if (!response.ok) {
    throw new Error('Failed to search IPs')
  }
  const result: APIResponse<IP[]> = await response.json()
  return result.data
}

// 获取所有IP（分页）
export const getAllIPs = async (
  limit: number = 50,
  offset: number = 0
): Promise<IP[]> => {
  const response = await fetch(
    `${BASE_API_URL}/api/ip?limit=${limit}&offset=${offset}`
  )
  if (!response.ok) {
    throw new Error('Failed to fetch all IPs')
  }
  const result: APIResponse<IP[]> = await response.json()
  return result.data
}