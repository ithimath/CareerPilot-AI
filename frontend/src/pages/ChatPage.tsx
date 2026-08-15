import React, { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import {
  Send, Plus, MessageSquare, Trash2, Loader, Bot, User, Copy, Check, Sparkles,
  RefreshCw, Menu, X, ArrowRight
} from 'lucide-react'
import toast from 'react-hot-toast'

// Formats basic markdown content (headings, bold, lists, inline code, quotes) into rich HTML elements
function FormattedMessageContent({ content }: { content: string }) {
  const lines = content.split('\n')
  const elements: React.ReactNode[] = []

  let inList = false
  let listItems: React.ReactNode[] = []
  let listType: 'ul' | 'ol' = 'ul'

  const flushList = () => {
    if (inList && listItems.length > 0) {
      if (listType === 'ul') {
        elements.push(
          <ul key={`list-${elements.length}`} className="my-2 space-y-1 pl-4 list-disc marker:text-[#FF5722]">
            {listItems}
          </ul>
        )
      } else {
        elements.push(
          <ol key={`list-${elements.length}`} className="my-2 space-y-1 pl-4 list-decimal marker:text-[#FF5722] font-semibold">
            {listItems}
          </ol>
        )
      }
      listItems = []
      inList = false
    }
  }

  const renderInline = (text: string) => {
    // Replace **bold** and `code`
    const parts = []
    let cursor = 0
    // Regex matching **bold**, `code`, and [link](url)
    const regex = /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\))/g
    let match: RegExpExecArray | null

    while ((match = regex.exec(text)) !== null) {
      if (match.index > cursor) {
        parts.push(text.substring(cursor, match.index))
      }
      if (match[2]) {
        // **bold**
        parts.push(<strong key={`b-${cursor}`} className="font-bold text-app">{match[2]}</strong>)
      } else if (match[3]) {
        // `code`
        parts.push(
          <code key={`c-${cursor}`} className="px-1.5 py-0.5 rounded bg-subtle border border-app text-[11px] font-mono text-[#FF5722] dark:text-[#FF7043]">
            {match[3]}
          </code>
        )
      } else if (match[4] && match[5]) {
        // [link](url)
        parts.push(
          <a
            key={`a-${cursor}`}
            href={match[5]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#FF5722] underline hover:text-[#E64A19] font-semibold"
          >
            {match[4]}
          </a>
        )
      }
      cursor = regex.lastIndex
    }

    if (cursor < text.length) {
      parts.push(text.substring(cursor))
    }

    return parts.length > 0 ? parts : text
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim()

    // Heading 3
    if (trimmed.startsWith('### ')) {
      flushList()
      elements.push(
        <h4 key={index} className="font-heading text-sm font-bold text-[#FF5722] dark:text-[#FF7043] mt-3 mb-1 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          {trimmed.replace('### ', '')}
        </h4>
      )
      return
    }

    // Heading 4 / Subheading
    if (trimmed.startsWith('#### ')) {
      flushList()
      elements.push(
        <h5 key={index} className="font-heading text-xs font-bold text-app mt-2 mb-1">
          {trimmed.replace('#### ', '')}
        </h5>
      )
      return
    }

    // Unordered List item
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      if (!inList || listType !== 'ul') {
        flushList()
        inList = true
        listType = 'ul'
      }
      const itemText = trimmed.replace(/^[-*•]\s+/, '')
      listItems.push(
        <li key={`item-${index}`} className="text-xs leading-relaxed text-app">
          {renderInline(itemText)}
        </li>
      )
      return
    }

    // Ordered List item (e.g. "1. ")
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/)
    if (numMatch) {
      if (!inList || listType !== 'ol') {
        flushList()
        inList = true
        listType = 'ol'
      }
      listItems.push(
        <li key={`item-${index}`} className="text-xs leading-relaxed text-app">
          {renderInline(numMatch[2])}
        </li>
      )
      return
    }

    // Empty line
    if (!trimmed) {
      flushList()
      elements.push(<div key={index} className="h-1.5" />)
      return
    }

    // Regular paragraph
    flushList()
    elements.push(
      <p key={index} className="text-xs leading-relaxed text-app my-0.5">
        {renderInline(trimmed)}
      </p>
    )
  })

  flushList()

  return <div className="space-y-0.5">{elements}</div>
}

function MessageBubble({ message }: { message: any }) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    if (!message.content) return
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    toast.success('Response copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`flex gap-3 group ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg shadow-xs ${
        isUser ? 'bg-[#FF5722] text-white' : 'bg-[#FF5722]/10 border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:border-[#FF5722]/40'
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />}
      </div>
      
      <div className={`relative max-w-[85%] md:max-w-[78%] px-4 py-3 text-xs rounded-2xl shadow-xs transition-all ${
        isUser
          ? 'bg-[#FF5722] text-white font-medium rounded-tr-xs'
          : 'bg-subtle text-app border border-app rounded-tl-xs'
      }`}>
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <div>
            <FormattedMessageContent content={message.content} />
            <div className="mt-2 pt-2 border-t border-app/40 flex items-center justify-between text-[10px] text-secondary">
              <span className="flex items-center gap-1 font-semibold text-[#FF5722] dark:text-[#FF7043]">
                <Sparkles className="w-3 h-3" /> CareerPilot AI
              </span>
              <button
                onClick={copyToClipboard}
                className="opacity-60 hover:opacity-100 hover:text-app flex items-center gap-1 px-1.5 py-0.5 rounded transition-all cursor-pointer"
                title="Copy response"
              >
                {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          </div>
        )}
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
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Conversations list
  const { data: convsData, isLoading: loadingConvs } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => api.get('/api/chat/conversations').then((r) => r.data),
  })

  // Load conversation messages when switching
  const loadConversation = async (convId: string) => {
    setCurrentConvId(convId)
    setMobileSidebarOpen(false)
    try {
      const res = await api.get(`/api/chat/conversations/${convId}`)
      setMessages(res.data.messages || [])
    } catch {
      setMessages([])
    }
  }

  const newConvMutation = useMutation({
    mutationFn: () => api.post('/api/chat/conversations', { title: 'New Strategy Session' }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      const newId = res.data.id || 'conv_' + Date.now()
      setCurrentConvId(newId)
      setMessages([
        {
          role: 'assistant',
          content: 'Hello! I am your CareerPilot AI Strategist. What career, resume, or technical goals would you like to work on today?'
        }
      ])
      setMobileSidebarOpen(false)
    },
    onError: () => {
      toast.error('Failed to create session')
    }
  })

  const deleteConvMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/chat/conversations/${id}`),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      if (currentConvId === deletedId) {
        setCurrentConvId(null)
        setMessages([])
      }
      toast.success('Session removed')
    },
    onError: () => {
      toast.error('Could not remove session')
    }
  })

  const sendMessage = async (textToSend?: string) => {
    const text = textToSend || input
    if (!text.trim() || sending) return

    let convId = currentConvId
    if (!convId) {
      try {
        const res = await api.post('/api/chat/conversations', { title: text.slice(0, 35) })
        convId = res.data.id || 'conv_' + Date.now()
        setCurrentConvId(convId)
        queryClient.invalidateQueries({ queryKey: ['conversations'] })
      } catch {
        convId = 'conv_' + Date.now()
        setCurrentConvId(convId)
      }
    }

    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    if (!textToSend) setInput('')
    setSending(true)

    try {
      const res = await api.post(`/api/chat/conversations/${convId}/message`, { message: text })
      if (res.data && res.data.messages) {
        setMessages(res.data.messages)
      } else {
        // Fallback if structured response format differs
        const reply = res.data.reply || 'Insight generated successfully.'
        setMessages((prev) => [...prev, { role: 'assistant', content: reply, timestamp: new Date().toISOString() }])
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || err.message || 'Mentor response failed. Retrying...')
    } finally {
      setSending(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const convs = convsData?.conversations || []

  return (
    <div className="h-[calc(100vh-6.5rem)] flex gap-4 animate-fade-in text-app relative">
      {/* Mobile Drawer Overlay */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar: Conversation history */}
      <div className={`
        fixed md:static inset-y-0 left-0 z-50 md:z-auto w-72 md:w-64 card flex flex-col p-3 space-y-3 bg-surface transition-transform duration-300
        ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="flex items-center justify-between pb-1 border-b border-app/60 md:border-none">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#FF5722]" />
            <span className="font-heading text-xs font-bold text-app">Chat History</span>
          </div>
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="md:hidden p-1 text-secondary hover:text-app"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <button
          onClick={() => newConvMutation.mutate()}
          disabled={newConvMutation.isPending}
          className="btn btn-primary text-xs w-full gap-2 justify-center py-2 shadow-xs cursor-pointer"
        >
          <Plus className="w-4 h-4" /> New Strategy Session
        </button>

        <div className="flex-1 overflow-y-auto space-y-1.5 pr-0.5 custom-scrollbar">
          {loadingConvs ? (
            <div className="flex items-center justify-center p-6 text-xs text-secondary gap-2">
              <Loader className="w-3.5 h-3.5 animate-spin text-[#FF5722]" />
              <span>Loading sessions...</span>
            </div>
          ) : convs.length === 0 ? (
            <div className="text-center py-8 px-2 text-xs text-secondary">
              <p className="font-medium">No previous sessions</p>
              <p className="text-[10px] mt-1 text-secondary/70">Start a new conversation to plan your career path.</p>
            </div>
          ) : (
            convs.map((conv: any) => (
              <div
                key={conv.id}
                onClick={() => loadConversation(conv.id)}
                className={`group flex items-center justify-between gap-2 px-3 py-2.5 text-xs cursor-pointer transition-all rounded-lg ${
                  conv.id === currentConvId
                    ? 'bg-[#FF5722]/10 text-[#FF5722] font-bold border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043]'
                    : 'text-secondary hover:bg-subtle hover:text-app'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare className="w-3.5 h-3.5 flex-shrink-0 text-[#FF5722] dark:text-[#FF7043]" />
                  <span className="truncate">{conv.title || 'Career Strategy Session'}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteConvMutation.mutate(conv.id)
                  }}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition-all p-1"
                  title="Delete session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main chat window */}
      <div className="flex-1 card flex flex-col justify-between overflow-hidden bg-surface">
        {/* Header */}
        <div className="p-3.5 md:p-4 border-b border-app flex items-center justify-between bg-surface">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="md:hidden p-1.5 rounded-lg border border-app text-secondary hover:text-app"
            >
              <Menu className="w-4 h-4" />
            </button>
            
            <div className="w-9 h-9 bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] rounded-lg flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-[#FF5722] dark:text-[#FF7043]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-heading text-sm font-bold text-app">AI Career Strategist & Mentor</p>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/10 text-green-700 dark:text-green-400 border border-green-500/20">
                  Online
                </span>
              </div>
              <p className="text-[11px] text-secondary font-medium">Context-aware candidate evaluation, skill gap diagnostics & interview coaching</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={() => setMessages([])}
                className="btn btn-outline text-xs px-2.5 py-1.5 gap-1 text-secondary hover:text-app hidden sm:flex"
                title="Clear current view"
              >
                <RefreshCw className="w-3 h-3" /> Clear
              </button>
            )}
          </div>
        </div>

        {/* Message feed */}
        <div className="flex-1 p-4 md:p-6 overflow-y-auto space-y-4 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-4 md:p-8 space-y-5 max-w-xl mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-[#FF5722]/10 border border-[#FF5722]/30 flex items-center justify-center shadow-xs">
                <Bot className="w-8 h-8 text-[#FF5722]" />
              </div>
              <div>
                <h3 className="font-heading text-xl font-bold text-app">AI Career Advisor Ready</h3>
                <p className="text-xs text-secondary max-w-md mt-1.5 leading-relaxed font-medium">
                  Ask deep questions about skill gaps, resume keywords, system design patterns, or career track alignment tailored to your target job profile.
                </p>
              </div>

              {/* Quick prompts */}
              <div className="w-full space-y-2 pt-2">
                <p className="text-[10px] font-bold uppercase tracking-wider text-secondary text-left">Sample Strategy Prompts</p>
                <div className="grid grid-cols-1 gap-2">
                  {QUICK_PROMPTS.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(prompt)}
                      className="w-full p-3 bg-subtle border border-app rounded-xl text-left text-xs font-semibold text-app hover:border-[#FF5722] hover:bg-surface-hover transition-all flex items-center justify-between group cursor-pointer"
                    >
                      <span className="pr-2">{prompt}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-secondary group-hover:text-[#FF5722] group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <MessageBubble key={i} message={msg} />
              ))}
              {sending && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-[#FF5722]/10 border border-[#FF5722]/30 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-[#FF5722] dark:text-[#FF7043]" />
                  </div>
                  <div className="p-3.5 bg-subtle border border-app rounded-2xl rounded-tl-xs text-xs text-secondary flex items-center gap-2 shadow-xs">
                    <Loader className="w-4 h-4 animate-spin text-[#FF5722] dark:text-[#FF7043]" />
                    <span className="font-medium">Synthesizing personalized career insights & roadmap...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input box */}
        <div className="p-3 md:p-4 border-t border-app bg-surface space-y-2">
          {messages.length > 0 && (
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] custom-scrollbar">
              <span className="text-secondary font-semibold text-[10px] uppercase tracking-wider flex-shrink-0">Suggested:</span>
              <button
                onClick={() => sendMessage('What specific skills should I learn next?')}
                className="px-2.5 py-1 rounded-full bg-subtle hover:bg-surface-hover border border-app text-app whitespace-nowrap transition-colors cursor-pointer"
              >
                Next Skills
              </button>
              <button
                onClick={() => sendMessage('Give me a 30-day preparation checklist')}
                className="px-2.5 py-1 rounded-full bg-subtle hover:bg-surface-hover border border-app text-app whitespace-nowrap transition-colors cursor-pointer"
              >
                30-Day Plan
              </button>
              <button
                onClick={() => sendMessage('How do I optimize my projects for ATS?')}
                className="px-2.5 py-1 rounded-full bg-subtle hover:bg-surface-hover border border-app text-app whitespace-nowrap transition-colors cursor-pointer"
              >
                ATS Projects
              </button>
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage()
            }}
            className="flex items-center gap-2"
          >
            <input
              className="input text-xs flex-1 py-2.5 px-3.5 rounded-xl border border-app bg-subtle focus:bg-surface"
              placeholder="Ask AI Career Mentor anything (e.g. system design, resume audit, skill roadmap)..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!input.trim() || sending}
              className="btn btn-primary px-4 py-2.5 rounded-xl cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
