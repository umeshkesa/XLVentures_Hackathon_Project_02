import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { RecommendationItem, RecommendationSummary } from '@/types/recommendations'

interface RecommendationListResponse {
  recommendations?: RecommendationItem[]
  total?: number
}

export interface UseRecommendationParams {
  status?: string
  priority?: string
  source?: string
  search?: string
  page?: number
  limit?: number
}

export function useRecommendationList(params: UseRecommendationParams) {
  return useQuery({
    queryKey: ['recommendations', params],
    queryFn: async () => {
      const { data } = await apiGet<RecommendationListResponse>('/recommendation', {
        status: params.status,
        priority: params.priority,
        source: params.source,
        search: params.search ?? '',
        page: params.page ?? 1,
        limit: params.limit ?? 12,
      })
      const items = data?.recommendations ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useRecommendationById(id: string) {
  return useQuery({
    queryKey: ['recommendations', id],
    queryFn: async () => {
      const { data } = await apiGet<RecommendationItem>(`/recommendation/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useRecommendationSummary() {
  return useQuery({
    queryKey: ['recommendations', 'summary'],
    queryFn: async () => {
      const { data } = await apiGet<RecommendationListResponse>('/recommendation', { limit: 100 })
      const items = data?.recommendations ?? []
      return {
        active: items.filter((r) => r.status === 'active').length,
        pendingApproval: items.filter((r) => r.status === 'pending_approval').length,
        approved: items.filter((r) => r.status === 'approved').length,
        rejected: items.filter((r) => r.status === 'rejected').length,
        executed: items.filter((r) => r.status === 'executed').length,
        draft: items.filter((r) => r.status === 'draft').length,
        totalCost: items.reduce((a, r) => a + (r.estimatedCost || 0), 0),
        totalSavings: items.reduce((a, r) => a + (r.estimatedSavings || 0), 0),
      } as RecommendationSummary
    },
    staleTime: 30_000,
    retry: 2,
  })
}
