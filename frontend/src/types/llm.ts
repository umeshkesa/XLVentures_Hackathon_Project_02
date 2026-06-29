export interface LLMMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface Conversation {
  id: string
  title: string
  messages: LLMMessage[]
  createdAt: string
  updatedAt: string
}

export interface SuggestedQuestion {
  id: string
  text: string
  category: string
}
