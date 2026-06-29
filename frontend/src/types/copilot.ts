export interface CopilotMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: CopilotSource[]
  confidence?: number
  processingTime?: number
}

export interface CopilotSource {
  type: 'evidence' | 'knowledge' | 'rule' | 'recommendation' | 'reasoning' | 'asset' | 'interaction'
  id: string
  title: string
  relevance: number
}

export interface CopilotConversation {
  id: string
  title: string
  lastMessage: string
  messageCount: number
  timestamp: string
}

export interface CopilotSuggestion {
  id: string
  text: string
  category: string
  icon?: string
}
