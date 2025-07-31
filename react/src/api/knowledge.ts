import { authenticatedFetch } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 知识库基本信息接口
export const getKnowledgeList = async (): Promise<string[]> => {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/api/knowledge`)
    if (!response.ok) {
      throw new Error('Failed to fetch knowledge list')
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching knowledge list:', error)
    return []
  }
}

// 获取单个知识库文件内容
export const getKnowledgeDetail = async (path: string): Promise<string> => {
  try {
    const response = await authenticatedFetch(
      `${API_BASE_URL}/api/knowledge/detail?path=${path}`
    )
    if (!response.ok) {
      throw new Error('Failed to fetch knowledge detail')
    }
    const data = await response.json()
    return data.content
  } catch (error) {
    console.error('Error fetching knowledge detail:', error)
    return ''
  }
}

// 创建或更新知识库文件
export const updateKnowledge = async (
  path: string,
  content: string
): Promise<void> => {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/api/knowledge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path, content }),
    })
    if (!response.ok) {
      throw new Error('Failed to update knowledge')
    }
  } catch (error) {
    console.error('Error updating knowledge:', error)
    throw error
  }
}

// 删除知识库文件
export const deleteKnowledge = async (path: string): Promise<void> => {
  try {
    const response = await authenticatedFetch(
      `${API_BASE_URL}/api/knowledge?path=${path}`,
      {
        method: 'DELETE',
      }
    )
    if (!response.ok) {
      throw new Error('Failed to delete knowledge')
    }
  } catch (error) {
    console.error('Error deleting knowledge:', error)
    throw error
  }
}
