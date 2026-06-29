import { useState, useRef, useEffect } from 'react'
import { useCopilotSuggestions, useSendCopilotMessage } from '@/services/copilotApiService'
import type { CopilotMessage } from '@/types/copilot'
import { cn } from '@/lib/utils'
import {
  Sparkles, Send, Bot, User, Trash2, Copy, Check, ArrowRight, MessageSquare,
  FileSearch, BookOpen, Scale, ThumbsUp, HardDrive, Zap, Upload,
} from 'lucide-react'
import { LoadingSpinner } from '@/components/LoadingSpinner'

function Markdown({ text }: { text: string }) {
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let tableRows: string[][] = []
  let isInsideTable = false
  let codeBlock: string[] = []
  let isInsideCode = false
  let codeLanguage = ''

  const flushTable = (key: number) => {
    if (tableRows.length === 0) return null
    const headers = tableRows[0]
    const rows = tableRows.slice(2)
    tableRows = []
    isInsideTable = false
    return (
      <div key={`t-${key}`} className="my-3 overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-xs text-left border-collapse">
          <thead><tr className="bg-muted/70 border-b border-border">{headers.map((h, i) => (<th key={i} className="p-2 font-semibold text-foreground">{parseInline(h.trim())}</th>))}</tr></thead>
          <tbody className="divide-y divide-border">{rows.map((row, ri) => (<tr key={ri} className="hover:bg-muted/30">{row.map((cell, ci) => (<td key={ci} className="p-2 text-muted-foreground">{parseInline(cell.trim())}</td>))}</tr>))}</tbody>
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
        if (boldMatch.index > 0) parts.push(currentText.substring(0, boldMatch.index))
        parts.push(<strong key={index++} className="font-bold text-foreground">{boldMatch[1]}</strong>)
        currentText = currentText.substring(boldMatch.index + boldMatch[0].length)
      } else { parts.push(currentText); break }
    }
    return parts.length === 1 ? parts[0] : <>{parts}</>
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim()

    if (trimmed.startsWith('```')) {
      if (isInsideCode) {
        elements.push(
          <div key={`cb-${index}`} className="my-3 rounded-lg overflow-hidden border border-border">
            <div className="flex items-center justify-between bg-muted/80 px-3 py-1.5 border-b border-border">
              <span className="text-[10px] font-mono text-muted-foreground">{codeLanguage || 'code'}</span>
              <button onClick={() => { navigator.clipboard.writeText(codeBlock.join('\n')) }}
                className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors">
                <Copy className="h-3 w-3" /> Copy
              </button>
            </div>
            <pre className="bg-muted/30 p-3 overflow-x-auto"><code className="text-[11px] font-mono leading-relaxed">{codeBlock.join('\n')}</code></pre>
          </div>
        )
        codeBlock = []
        isInsideCode = false
        codeLanguage = ''
      } else {
        codeLanguage = trimmed.slice(3).trim()
        isInsideCode = true
      }
      return
    }
    if (isInsideCode) { codeBlock.push(line); return }

    if (trimmed.startsWith('|')) {
      isInsideTable = true
      tableRows.push(trimmed.split('|').slice(1, -1))
      return
    }
    if (isInsideTable && !trimmed.startsWith('|')) { const t = flushTable(index); if (t) elements.push(t) }

    if (trimmed.startsWith('## ')) { elements.push(<h3 key={index} className="text-sm font-bold text-foreground mt-4 mb-1.5 border-b pb-1">{parseInline(trimmed.slice(3))}</h3>); return }
    if (trimmed.startsWith('### ')) { elements.push(<h4 key={index} className="text-xs font-bold text-foreground mt-3 mb-1">{parseInline(trimmed.slice(4))}</h4>); return }
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) { elements.push(<ul key={index} className="list-disc pl-4 text-xs space-y-1 my-1 text-muted-foreground"><li>{parseInline(trimmed.slice(2))}</li></ul>); return }
    const numMatch = trimmed.match(/^(\d+)\.\s(.*)/)
    if (numMatch) { elements.push(<ol key={index} className="list-decimal pl-4 text-xs space-y-1 my-1 text-muted-foreground"><li value={parseInt(numMatch[1])}>{parseInline(numMatch[2])}</li></ol>); return }
    if (!trimmed) { elements.push(<div key={index} className="h-2" />); return }
    elements.push(<p key={index} className="text-xs leading-relaxed text-muted-foreground mb-1">{parseInline(trimmed)}</p>)
  })
  if (isInsideTable) { const t = flushTable(lines.length); if (t) elements.push(t) }
  if (isInsideCode) { elements.push(<pre key="cb-end" className="bg-muted/30 p-3 rounded-lg overflow-x-auto text-[11px] font-mono"><code>{codeBlock.join('\n')}</code></pre>) }
  return <div className="space-y-1">{elements}</div>
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  recommendations: <ThumbsUp className="h-3.5 w-3.5" />,
  customers: <MessageSquare className="h-3.5 w-3.5" />,
  knowledge: <BookOpen className="h-3.5 w-3.5" />,
  evidence: <FileSearch className="h-3.5 w-3.5" />,
  rules: <Scale className="h-3.5 w-3.5" />,
  assets: <HardDrive className="h-3.5 w-3.5" />,
  import: <Upload className="h-3.5 w-3.5" />,
  platform: <Zap className="h-3.5 w-3.5" />,
}

export default function AICopilot() {
  const [messages, setMessages] = useState<CopilotMessage[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const sendMutation = useSendCopilotMessage()
  const { data: suggestions = [] } = useCopilotSuggestions()

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async (text: string) => {
    if (!text.trim() || sendMutation.isPending) return
    const userMsg: CopilotMessage = { id: `msg-${Date.now()}-user`, role: 'user', content: text, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    try {
      const result = await sendMutation.mutateAsync({ message: text, conversationId })
      const t0 = performance.now()
      const assistantMsg: CopilotMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: result?.response ?? 'No response received.',
        timestamp: new Date().toISOString(),
        confidence: 0.87,
        processingTime: Math.round((performance.now() - t0) / 10) / 100,
        sources: [],
      }
      setConversationId(result?.conversation_id ?? null)
      setMessages(prev => [...prev, assistantMsg])
    } catch {
      setMessages(prev => [...prev, { id: `msg-err-${Date.now()}`, role: 'assistant', content: 'Error: Failed to get response from the AI coordinator. Please check connectivity.', timestamp: new Date().toISOString() }])
    }
  }

  const handleClear = () => { setMessages([]); setConversationId(null) }

  const handleCopy = (content: string, id: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const showWelcome = messages.length === 0

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-0">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b bg-card px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold">AI Copilot</h1>
              <p className="text-xs text-muted-foreground">Ask questions about assets, evidence, rules, and recommendations</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button onClick={handleClear} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground px-3 py-1.5 rounded-lg hover:bg-muted transition-colors">
              <Trash2 className="h-3.5 w-3.5" /> Clear
            </button>
          )}
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {showWelcome ? (
            <div className="max-w-2xl mx-auto pt-8 space-y-8">
              <div className="text-center space-y-3">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <Bot className="h-8 w-8" />
                </div>
                <h2 className="text-xl font-bold">ADIP AI Copilot</h2>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Ask me about any aspect of the ADIP platform — assets, evidence, business rules, reasoning, recommendations, or platform health.
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-xl mx-auto">
                {suggestions.map((q) => (
                  <button key={q.id} onClick={() => handleSend(q.text)}
                    className="flex items-center gap-2 text-left p-3 rounded-xl border bg-card hover:border-primary/40 hover:bg-muted/30 text-xs transition-all group"
                  >
                    <span className="shrink-0 text-muted-foreground">{CATEGORY_ICONS[q.category] ?? <Sparkles className="h-3.5 w-3.5" />}</span>
                    <span className="text-muted-foreground group-hover:text-foreground line-clamp-2 flex-1">{q.text}</span>
                    <ArrowRight className="h-3 w-3 shrink-0 text-muted-foreground/60 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={cn('flex gap-3', msg.role === 'assistant' ? '' : 'flex-row-reverse')}>
                  <div className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border text-xs', msg.role === 'assistant' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground')}>
                    {msg.role === 'assistant' ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>
                  <div className={cn('max-w-[80%] space-y-2', msg.role === 'assistant' ? '' : 'flex flex-col items-end')}>
                    <div className={cn('rounded-2xl px-4 py-3 shadow-xs border', msg.role === 'assistant' ? 'bg-card text-card-foreground border-border' : 'bg-primary text-primary-foreground border-primary')}>
                      {msg.role === 'assistant' ? (
                        <div className="space-y-1">
                          <Markdown text={msg.content} />
                          {msg.processingTime && (
                            <div className="flex items-center gap-2 pt-2 mt-2 border-t border-border/50">
                              <span className="text-[10px] text-muted-foreground/60">{msg.processingTime.toFixed(1)}s</span>
                              {msg.confidence && <span className="text-[10px] text-muted-foreground/60">Confidence: {Math.round(msg.confidence * 100)}%</span>}
                            </div>
                          )}
                            {(msg.sources && msg.sources.length > 0) && (
                            <div className="flex flex-wrap gap-1.5 pt-2 mt-2 border-t border-border/50">
                              <span className="text-[10px] text-muted-foreground font-medium">Sources:</span>
                              {msg.sources.map((s, i) => (
                                <span key={i} className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] border bg-muted/30 text-muted-foreground">{s.type}:{s.id}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 px-1">
                      <span className="text-[10px] text-muted-foreground/50">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      {msg.role === 'assistant' && (
                        <button onClick={() => handleCopy(msg.content, msg.id)} className="text-muted-foreground/50 hover:text-foreground transition-colors" title="Copy response">
                          {copiedId === msg.id ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {sendMutation.isPending && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="bg-card border rounded-2xl px-4 py-3 shadow-xs">
                    <div className="flex items-center gap-2">
                      <LoadingSpinner size="sm" />
                      <span className="text-xs text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
        <div className="border-t bg-card px-6 py-4">
          <form onSubmit={(e) => { e.preventDefault(); handleSend(input) }} className="flex items-center gap-3 max-w-3xl mx-auto">
            <input ref={inputRef} type="text" placeholder="Ask a question about the platform..." value={input} onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-background border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" disabled={sendMutation.isPending} />
            <button type="submit" disabled={!input.trim() || sendMutation.isPending}
              className="h-10 w-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 transition-all">
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
