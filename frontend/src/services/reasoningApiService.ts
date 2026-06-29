import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { ReasoningSession, ReasoningSummary, ReasoningStatus, ReasoningDomain } from '@/types/reasoning'

interface ReasoningListResponse {
  reasonings?: ReasoningSession[]
  total?: number
}

export interface UseReasoningParams {
  status?: ReasoningStatus
  domain?: ReasoningDomain
  search?: string
  page?: number
  limit?: number
}

export function useReasoningList(params: UseReasoningParams) {
  return useQuery({
    queryKey: ['reasoning', params],
    queryFn: async () => {
      const { data } = await apiGet<ReasoningListResponse>('/reasoning', {
        status: params.status,
        domain: params.domain,
        search: params.search ?? '',
        page: params.page ?? 1,
        limit: params.limit ?? 12,
      })
      const items = data?.reasonings ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useReasoningById(id: string) {
  return useQuery({
    queryKey: ['reasoning', id],
    queryFn: async () => {
      const { data } = await apiGet<ReasoningSession>(`/reasoning/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useReasoningSummary() {
  return useQuery({
    queryKey: ['reasoning', 'summary'],
    queryFn: async () => {
      const { data } = await apiGet<ReasoningListResponse>('/reasoning', { limit: 100 })
      const items = data?.reasonings ?? []
      const completed = items.filter((s) => s.status === 'completed')
      return {
        activeCount: items.filter((s) => s.status === 'in_progress').length,
        completedCount: completed.length,
        failedCount: items.filter((s) => s.status === 'failed').length,
        averageConfidence: completed.length > 0
          ? parseFloat((completed.reduce((a, s) => a + s.confidence, 0) / completed.length).toFixed(3))
          : 0,
        averageRiskScore: completed.length > 0
          ? parseFloat((completed.reduce((a, s) => a + s.riskScore, 0) / completed.length).toFixed(3))
          : 0,
      } as ReasoningSummary
    },
    staleTime: 30_000,
    retry: 2,
  })
}
