import { Message, Model } from '@/types/types'
import { ModelInfo, ToolInfo } from './model'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://jaaz-backend-337074826438.asia-northeast1.run.app'

export const getChatSession = async (sessionId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/chat_session/${sessionId}`)
  const data = await response.json()
  return data as Message[]
}

export const sendMessages = async (payload: {
  sessionId: string
  canvasId: string
  newMessages: Message[]
  textModel: Model
  toolList: ToolInfo[]
  systemPrompt: string | null
}) => {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: payload.newMessages,
      canvas_id: payload.canvasId,
      session_id: payload.sessionId,
      text_model: payload.textModel,
      tool_list: payload.toolList,
      system_prompt: payload.systemPrompt,
    }),
  })
  const data = await response.json()
  return data as Message[]
}

export const cancelChat = async (sessionId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/cancel/${sessionId}`, {
    method: 'POST',
  })
  return await response.json()
}
