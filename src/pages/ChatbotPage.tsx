import { useState, useRef, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { sendChatMessage } from '../services/api'
import type { ChatRequest } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Send, Bot, User } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  timestamp: Date
}

export default function ChatbotPage() {
  const location = useLocation()
  const dbtiType = location.state?.dbtiType

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: dbtiType
        ? `안녕하세요! 🐾 ${dbtiType} 유형에 대해 궁금하신 점이나 양육 방법에 대해 무엇이든 물어보세요!`
        : '안녕하세요! 🐾 DBTI 챗봇입니다. 강아지 양육에 대해 무엇이든 물어보세요!',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [dbti, setDbti] = useState(dbtiType || '')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const chatMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.message,
          sources: data.sources,
          timestamp: new Date(),
        },
      ])
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요.',
          timestamp: new Date(),
        },
      ])
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || chatMutation.isPending) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')

    const request: ChatRequest = {
      message: input,
      dbti_type: dbti || undefined,
      conversation_history: messages.slice(-5).map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
    }

    chatMutation.mutate(request)
  }

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="w-6 h-6 text-primary" />
              DBTI AI 챗봇
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium">DBTI 유형 (선택)</label>
              <input
                type="text"
                value={dbti}
                onChange={(e) => setDbti(e.target.value.toUpperCase())}
                placeholder="예: CNEA"
                maxLength={4}
                className="px-3 py-1 border rounded-md w-32 uppercase"
              />
              <span className="text-sm text-muted-foreground">
                유형을 입력하면 맞춤 답변을 받을 수 있어요
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Messages */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="h-[500px] overflow-y-auto space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                        <Bot className="w-5 h-5 text-primary-foreground" />
                      </div>
                    </div>
                  )}

                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border/50">
                        <p className="text-xs text-muted-foreground mb-1">
                          📚 참고 자료:
                        </p>
                        <ul className="text-xs space-y-1">
                          {message.sources.map((source, i) => (
                            <li key={i}>• {source}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <p className="text-xs opacity-60 mt-1">
                      {message.timestamp.toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                        <User className="w-5 h-5" />
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {chatMutation.isPending && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <Bot className="w-5 h-5 text-primary-foreground" />
                    </div>
                  </div>
                  <div className="bg-secondary rounded-lg px-4 py-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </CardContent>
        </Card>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요..."
            disabled={chatMutation.isPending}
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
          />
          <Button
            type="submit"
            size="lg"
            disabled={!input.trim() || chatMutation.isPending}
          >
            <Send className="w-5 h-5" />
          </Button>
        </form>
      </div>
    </div>
  )
}

