import { Message, Model } from '@/types/types'
import { ToolInfo } from './model'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const sendMagicGenerate = async (payload: {
  sessionId: string
  canvasId: string
  newMessages: Message[]
  systemPrompt: string | null
}) => {
  const response = await fetch(`${API_BASE_URL}/api/magic`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: payload.newMessages,
      canvas_id: payload.canvasId,
      session_id: payload.sessionId,
      system_prompt: payload.systemPrompt,
    }),
  })
  const data = await response.json()
  return data as Message[]
}

export const cancelMagicGenerate = async (sessionId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/api/magic/cancel/${sessionId}`,
    {
      method: 'POST',
    }
  )
  return await response.json()
}
