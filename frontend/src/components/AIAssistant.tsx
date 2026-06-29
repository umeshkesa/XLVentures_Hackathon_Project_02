import React, { useState, useRef } from 'react'
import {
  Sparkles,
  X,
  Send,
  Trash2,
  Bot,
  User,
  ArrowRight,
  Minus
} from 'lucide-react'
import { useSuggestedQuestions, useSendMessage } from '@/services/llmApiService'
import type { LLMMessage, SuggestedQuestion } from '@/types/llm'
import { cn } from '@/lib/utils'

// A simple but effective markdown parser for React to make demo text look premium
function Markdown({ text }: { text: string }) {
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let tableRows: string[][] = []
  let isInsideTable = false

  const flushTable = (key: number) => {
    if (tableRows.length === 0) return null
    const headers = tableRows[0]
    const rows = tableRows.slice(2) // Skip header separator line
    tableRows = []
    isInsideTable = false

    return (
      <div key={`table-${key}`} className="my-3 overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="bg-muted/70 border-b border-border">
              {headers.map((h, i) => (
                <th key={i} className="p-2 font-semibold text-foreground">
                  {parseInline(h.trim())}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-muted/30">
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="p-2 text-muted-foreground">
                    {parseInline(cell.trim())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const parseInline = (str: string): React.ReactNode => {
    const parts: React.ReactNode[] = []
    let currentText = str
    let index = 0

    while (currentText.length > 0) {
      const boldMatch = currentText.match(/\*\*(.*?)\*\*/)
      if (boldMatch && boldMatch.index !== undefined) {
        if (boldMatch.index > 0) {
          parts.push(currentText.substring(0, boldMatch.index))
        }
        parts.push(
          <strong key={index++} className="font-bold text-foreground">
            {boldMatch[1]}
          </strong>
        )
        currentText = currentText.substring(boldMatch.index + boldMatch[0].length)
      } else {
        parts.push(currentText)
        break
      }
    }
    return parts.length === 1 ? parts[0] : <>{parts}</>
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim()

    // Parse Tables
    if (trimmed.startsWith('|')) {
      isInsideTable = true
      const cols = trimmed
        .split('|')
        .slice(1, -1) // remove leading and trailing empty columns from split
      tableRows.push(cols)
      return
    }

    if (isInsideTable && !trimmed.startsWith('|')) {
      const table = flushTable(index)
      if (table) elements.push(table)
    }

    // Parse Headings
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={index} className="text-sm font-bold text-foreground mt-4 mb-1.5 border-b pb-1">
          {parseInline(trimmed.substring(3))}
        </h3>
      )
      return
    }
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={index} className="text-xs font-bold text-foreground mt-3 mb-1">
          {parseInline(trimmed.substring(4))}
        </h4>
      )
      return
    }

    // Parse Bullet Lists
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      elements.push(
        <ul key={index} className="list-disc pl-4 text-xs space-y-1 my-1 text-muted-foreground">
          <li>{parseInline(trimmed.substring(2))}</li>
        </ul>
      )
      return
    }

    // Parse Numbered Lists
    const numMatch = trimmed.match(/^(\d+)\.\s(.*)/)
    if (numMatch) {
      elements.push(
        <ol key={index} className="list-decimal pl-4 text-xs space-y-1 my-1 text-muted-foreground">
          <li value={parseInt(numMatch[1])}>{parseInline(numMatch[2])}</li>
        </ol>
      )
      return
    }

    // Blank line
    if (!trimmed) {
      elements.push(<div key={index} className="h-2" />)
      return
    }

    // Plain text
    elements.push(
      <p key={index} className="text-xs leading-relaxed text-muted-foreground mb-1">
        {parseInline(trimmed)}
      </p>
    )
  })

  // End of text table flush
  if (isInsideTable) {
    const table = flushTable(lines.length)
    if (table) elements.push(table)
  }

  return <div className="space-y-1">{elements}</div>
}

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<LLMMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)

  const sendMessageMutation = useSendMessage()
  const { data: apiSuggestions } = useSuggestedQuestions()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const suggestedQs: SuggestedQuestion[] = apiSuggestions?.length
    ? apiSuggestions.slice(0, 5)
    : []

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: LLMMessage = {
      id: `msg-temp-${Date.now()}-user`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const result = await sendMessageMutation.mutateAsync({ message: text, conversationId })
      const assistantMsg: LLMMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: result?.response ?? 'No response received.',
        timestamp: new Date().toISOString(),
      }
      setConversationId(result?.conversation_id ?? null)
      setMessages((prev) => [...prev, assistantMsg])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMsg: LLMMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'assistant',
        content: 'Error: Failed to get response from AI coordinator. Please check connectivity.',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setMessages([])
    setConversationId(null)
  }

  const togglePanel = () => {
    setIsOpen(!isOpen)
    setIsMinimized(false)
  }

  // Welcome message if conversation is empty
  const showWelcome = messages.length === 0

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={togglePanel}
          className="relative flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 group focus:outline-none focus:ring-2 focus:ring-primary/50"
          title="Open AI Assistant"
        >
          {/* Pulsing indicator */}
          <span className="absolute -right-0.5 -top-0.5 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-cyan-500"></span>
          </span>
          <Bot className="h-6 w-6 group-hover:rotate-6 transition-transform" />
        </button>
      )}

      {/* Main Chat Panel */}
      {isOpen && (
        <div
          className={cn(
            'flex flex-col rounded-2xl border bg-card text-card-foreground shadow-2xl transition-all duration-300 w-full sm:w-[420px] overflow-hidden',
            isMinimized ? 'h-14' : 'h-[550px]'
          )}
        >
          {/* Header */}
          <div className="flex h-14 items-center justify-between bg-primary px-4 text-primary-foreground">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10">
                <Sparkles className="h-4 w-4 text-cyan-300 fill-cyan-300/20" />
              </div>
              <div>
                <h3 className="text-sm font-semibold leading-none">ADIP Copilot</h3>
                <span className="text-[10px] text-cyan-200 mt-1 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400 inline-block animate-pulse"></span>
                  Decision Intelligence Coordinator
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="rounded-md p-1 hover:bg-white/10 text-primary-foreground/80 hover:text-white transition-colors"
                title={isMinimized ? 'Expand' : 'Minimize'}
              >
                <Minus className="h-4 w-4" />
              </button>
              {messages.length > 0 && !isMinimized && (
                <button
                  onClick={handleClear}
                  className="rounded-md p-1 hover:bg-white/10 text-primary-foreground/80 hover:text-white transition-colors"
                  title="Clear Chat"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
              <button
                onClick={togglePanel}
                className="rounded-md p-1 hover:bg-white/10 text-primary-foreground/80 hover:text-white transition-colors"
                title="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Panel Content (Visible only if not minimized) */}
          {!isMinimized && (
            <>
              {/* Message Thread */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20">
                {showWelcome ? (
                  <div className="space-y-4 py-4">
                    <div className="text-center space-y-2">
                      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <Bot className="h-6 w-6" />
                      </div>
                      <h4 className="text-sm font-semibold text-foreground">Welcome to ADIP Copilot</h4>
                      <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                        Ask me about business rules, asset metrics, evidence traceability, or recommendation explanations.
                      </p>
                    </div>

                    {/* Suggested Questions Grid */}
                    <div className="space-y-2">
                      <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider px-1">
                        Suggested Inquiries
                      </p>
                      <div className="space-y-1.5">
                        {suggestedQs.map((q) => (
                          <button
                            key={q.id}
                            onClick={() => handleSend(q.text)}
                            className="w-full text-left p-2.5 rounded-lg border bg-card hover:border-primary/40 hover:bg-muted/30 text-xs transition-all flex items-center justify-between group"
                          >
                            <span className="text-muted-foreground group-hover:text-foreground line-clamp-1">
                              {q.text}
                            </span>
                            <ArrowRight className="h-3 w-3 shrink-0 text-muted-foreground/60 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((msg) => {
                      const isBot = msg.role === 'assistant'
                      return (
                        <div
                          key={msg.id}
                          className={cn('flex gap-3 max-w-[85%]', isBot ? 'mr-auto' : 'ml-auto flex-row-reverse')}
                        >
                          <div
                            className={cn(
                              'flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs',
                              isBot ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                            )}
                          >
                            {isBot ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                          </div>
                          <div
                            className={cn(
                              'rounded-2xl px-3 py-2.5 text-xs shadow-xs border',
                              isBot
                                ? 'bg-card text-card-foreground border-border'
                                : 'bg-primary text-primary-foreground border-primary'
                            )}
                          >
                            {isBot ? (
                              <Markdown text={msg.content} />
                            ) : (
                              <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                            )}
                            <span
                              className={cn(
                                'text-[9px] block mt-1 text-right opacity-60',
                                isBot ? 'text-muted-foreground' : 'text-primary-foreground'
                              )}
                            >
                              {new Date(msg.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </div>
                        </div>
                      )
                    })}

                    {/* Typing/Thinking Animation */}
                    {isLoading && (
                      <div className="flex gap-3 max-w-[85%] mr-auto">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground border text-xs">
                          <Bot className="h-4 w-4" />
                        </div>
                        <div className="bg-card text-card-foreground border rounded-2xl px-3 py-3 shadow-xs">
                          <div className="flex items-center gap-1">
                            <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-bounce"></span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input */}
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSend(input)
                }}
                className="h-16 border-t bg-card px-4 flex items-center gap-2"
              >
                <input
                  type="text"
                  placeholder="Ask a question..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="flex-1 bg-background border rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="h-8 w-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 transition-all focus:outline-none"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </form>
            </>
          )}
        </div>
      )}
    </div>
  )
}
