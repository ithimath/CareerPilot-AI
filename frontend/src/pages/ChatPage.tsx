import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import {
  Send, Plus, MessageSquare, Trash2, Loader, Bot, User
} from 'lucide-react'
import toast from 'react-hot-toast'

function MessageBubble({ message }: { message: any }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-7 h-7 flex-shrink-0 flex items-center justify-center rounded-md ${
        isUser ? 'bg-teal-700 text-white' : 'bg-teal-50 border border-teal-200 dark:bg-teal-950/40 dark:border-teal-800'
      }`}>
        {isUser ? <User className="w-3.5 h-3.5 text-white" /> : <Bot className="w-3.5 h-3.5 text-teal-700 dark:text-teal-400" />}
      </div>
      <div className={`max-w-[75%] px-4 py-2.5 text-xs leading-relaxed rounded-xl ${
        isUser
          ? 'bg-teal-700 text-white shadow-xs font-medium'
          : 'bg-subtle text-app border border-app font-medium'
      }`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  )
}

const QUICK_PROMPTS = [
  'What technical skills should I master for Full-Stack role?',
  'Review my current resume ATS parser alignment',
  'Prepare me for a system design interview question',
  'Suggest high impact open source projects for my portfolio',
  'Audit my career readiness score matrix',
]

export default function ChatPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [currentConvId, setCurrentConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Conversations list
  const { data: convsData } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => api.get('/api/chat/conversations').then(r => r.data),
  })

  // Load conversation messages when switching
  const loadConversation = async (convId: string) => {
    setCurrentConvId(convId)
    try {
      const res = await api.get(`/api/chat/conversations/${convId}`)
      setMessages(res.data.messages || [])
    } catch {
      setMessages([])
    }
  }

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const deleteConvMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/chat/conversations/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      if (currentConvId) {
        setCurrentConvId(null)
        setMessages([])
      }
    },
  })

  const sendMessage = async (text?: string) => {
    const messageText = (text || input).trim()
    if (!messageText || sending) return
    setInput('')
    setSending(true)

    const userMsg = { role: 'user', content: messageText, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await api.post('/api/chat/send', {
        message: messageText,
        conversation_id: currentConvId,
        uid: user?.uid,
      })
      const { reply, conversation_id } = res.data
      setCurrentConvId(conversation_id)
      setMessages(prev => [...prev, { role: 'assistant', content: reply, timestamp: new Date().toISOString() }])
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    } catch (err: any) {
      toast.error(err.message || 'Failed to get response')
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setSending(false)
    }
  }

  const convs = convsData?.conversations || []

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4 animate-fade-in text-app">
      {/* Sidebar: conversations */}
      <div className="hidden md:flex w-56 flex-col gap-2 flex-shrink-0">
        <button
          onClick={() => { setCurrentConvId(null); setMessages([]) }}
          className="btn btn-primary text-xs gap-2 w-full justify-center"
        >
          <Plus className="w-3.5 h-3.5 text-white" /> New Session
        </button>

        <div className="flex-1 overflow-y-auto space-y-1">
          {convs.map((conv: any) => (
            <div
              key={conv.id}
              onClick={() => loadConversation(conv.id)}
              className={`group flex items-center gap-2 px-3 py-2 text-xs cursor-pointer transition-colors rounded-md ${
                conv.id === currentConvId
                  ? 'bg-teal-50 text-teal-900 font-bold border-l-2 border-teal-700 dark:bg-teal-950/40 dark:text-teal-300'
                  : 'text-secondary hover:bg-subtle'
              }`}
            >
              <MessageSquare className="w-3 h-3 flex-shrink-0 text-teal-700 dark:text-teal-400" />
              <span className="flex-1 truncate">{conv.title || 'New conversation'}</span>
              <button
                onClick={(e) => { e.stopPropagation(); deleteConvMutation.mutate(conv.id) }}
                className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition-all"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat window */}
      <div className="flex-1 card flex flex-col justify-between overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-app flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 rounded-md flex items-center justify-center">
              <Bot className="w-4 h-4 text-teal-700 dark:text-teal-400" />
            </div>
            <div>
              <p className="font-heading text-sm font-bold text-app">AI Career Strategist</p>
              <p className="text-[10px] text-secondary font-medium">Context-aware candidate evaluation mentor</p>
            </div>
          </div>
        </div>

        {/* Message feed */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
              <Bot className="w-10 h-10 text-secondary" />
              <div>
                <h3 className="font-heading text-xl font-bold text-app">AI Career Advisor Ready</h3>
                <p className="text-xs text-secondary max-w-sm mt-1 font-medium">
                  Ask questions about skill gaps, resume keywords, interview loops, or career track selection.
                </p>
              </div>

              {/* Quick prompts */}
              <div className="w-full max-w-md space-y-1.5 pt-2">
                <p className="text-[10px] font-bold uppercase tracking-wider text-secondary">Sample Strategy Prompts</p>
                {QUICK_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(prompt)}
                    className="w-full p-2.5 bg-subtle border border-app rounded-md text-left text-xs font-semibold text-app hover:border-teal-700 transition-all flex items-center justify-between"
                  >
                    <span>{prompt}</span>
                    <Send className="w-3 h-3 text-secondary" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <MessageBubble key={i} message={msg} />
              ))}
              {sending && (
                <div className="flex gap-3">
                  <div className="w-7 h-7 bg-teal-50 border border-teal-200 rounded-md flex items-center justify-center flex-shrink-0">
                    <Bot className="w-3.5 h-3.5 text-teal-700 dark:text-teal-400" />
                  </div>
                  <div className="p-3 bg-subtle border border-app rounded-md text-xs text-secondary flex items-center gap-2">
                    <Loader className="w-3.5 h-3.5 animate-spin text-teal-700 dark:text-teal-400" />
                    <span>Synthesizing career insights...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input box */}
        <div className="p-3 border-t border-app bg-surface">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage()
            }}
            className="flex items-center gap-2"
          >
            <input
              className="input text-xs flex-1"
              placeholder="Ask AI Career Mentor..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!input.trim() || sending}
              className="btn btn-primary p-2.5"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
