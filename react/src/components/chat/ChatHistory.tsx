import { Button } from '@/components/ui/button'
import { ChatSession } from '@/types/types'
import { XIcon } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function ChatHistory({
  sessionId,
  setSessionId,
  onClose,
}: {
  sessionId: string
  setSessionId: (sessionId: string) => void
  onClose: () => void
}) {
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  useEffect(() => {
    const fetchChatSessions = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://jaaz-backend-337074826438.asia-northeast1.run.app'
        console.log('📋 Loading chat sessions list from', API_BASE_URL)
        const sessions = await fetch(`${API_BASE_URL}/api/list_chat_sessions`, {
          headers: {
            'Content-Type': 'application/json',
          },
        })

        if (!sessions.ok) {
          console.error('❌ Failed to fetch chat sessions:', sessions.status, sessions.statusText)
          return
        }

        const data = await sessions.json()
        console.log('📋 Loaded chat sessions:', data.length)
        setChatSessions(data)
      } catch (error) {
        console.error('❌ Error loading chat sessions:', error)
      }
    }

    fetchChatSessions()
  }, [])
  return (
    <div className="flex flex-col bg-sidebar text-foreground w-[300px]">
      <div className="flex flex-col gap-4 p-3 sticky top-0 right-0 items-end">
        <Button variant={'ghost'} onClick={onClose} className="w-fit">
          <XIcon />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-3">
        <div className="flex flex-col text-left justify-start">
          {chatSessions.map((session) => (
            <Button
              key={session.id}
              variant={session.id === sessionId ? 'default' : 'ghost'}
              className="justify-start text-left px-2 w-full"
              onClick={() => {
                setSessionId(session.id)
              }}
            >
              <span className="truncate">{session.title || 'Untitled'}</span>
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
