export type KnowledgeCategory =
  | 'manual'
  | 'sop'
  | 'best_practice'
  | 'contract'
  | 'compliance'
  | 'policy'
  | 'article'
  | 'playbook'
  | 'pdf_document'

export type DocumentStatus = 'published' | 'draft' | 'archived'

export interface KnowledgeDocument {
  id: string
  title: string
  category: KnowledgeCategory
  status: DocumentStatus
  content: string
  summary: string
  author: string
  version: number
  createdAt: string
  updatedAt: string
  tags: string[]
  fileSize: number
  pageCount: number
  language: string
  sourceUrl: string
  relatedAssets: string[]
  relatedEvidence: string[]
  relatedRecommendations: string[]
}
