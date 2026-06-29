export type ReviewStatus = 'pending' | 'under_review' | 'more_info_needed' | 'approved' | 'rejected' | 'scheduled'
export type ReviewPriority = 'critical' | 'high' | 'medium' | 'low'

export interface ReviewComment {
  id: string
  author: string
  text: string
  timestamp: string
}

export interface AuditEntry {
  action: string
  by: string
  timestamp: string
  detail: string
}

export interface ReviewItem {
  review_id: string
  recommendation_id: string
  recommendation_title: string
  status: ReviewStatus
  priority: ReviewPriority
  assigned_engineer: string
  comments: ReviewComment[]
  audit_history: AuditEntry[]
  created_at: string
  updated_at: string
}

export interface ReviewSummary {
  pending: number
  underReview: number
  moreInfoNeeded: number
  approved: number
  rejected: number
  scheduled: number
  total: number
}
