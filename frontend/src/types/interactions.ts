export type InteractionType =
  | 'email'
  | 'meeting'
  | 'crm_update'
  | 'call_transcript'
  | 'chat'
  | 'complaint'
  | 'feedback'
  | 'service_request'

export type InteractionStatus = 'resolved' | 'pending' | 'escalated'

export interface Interaction {
  id: string
  type: InteractionType
  subject: string
  content: string
  date: string
  agent: string
  customerId: string
  customerName: string
  relatedAssets: string[]
  relatedEvidence: string[]
  relatedRecommendations: string[]
  relatedPlannerRun?: string | null
  attachments: { name: string; url: string; size: number }[]
  status: InteractionStatus
}

export interface InteractionTimelineGroup {
  date: string
  interactions: Interaction[]
}
