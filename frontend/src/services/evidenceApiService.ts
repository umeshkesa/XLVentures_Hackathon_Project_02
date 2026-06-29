import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { EvidenceType, EvidenceStatus, EvidencePriority, EvidenceItem, TraceabilityStep } from '@/types/evidence'

interface EvidenceQueryResponse {
  items?: EvidenceItem[]
  results?: EvidenceItem[]
  total?: number
}

export interface UseEvidenceParams {
  type?: EvidenceType
  status?: EvidenceStatus
  priority?: EvidencePriority
  search?: string
  page?: number
  limit?: number
  sort?: 'confidence' | 'date' | 'priority'
}

export interface UseEvidenceTraceabilityParams {
  evidenceId: string
}

export function useEvidence(params: UseEvidenceParams) {
  return useQuery({
    queryKey: ['evidence', params],
    queryFn: async () => {
      const { data } = await apiGet<EvidenceQueryResponse>('/evidence/query', {
        q: params.search ?? '',
        type: params.type,
        status: params.status,
        priority: params.priority,
        page: params.page,
        limit: params.limit,
        sort: params.sort,
      })
      const items = data?.items ?? data?.results ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30_000,
    retry: 2,
  })
}

export function useEvidenceById(id: string) {
  return useQuery({
    queryKey: ['evidence', id],
    queryFn: async () => {
      const { data } = await apiGet<EvidenceItem>(`/evidence/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useEvidenceTraceability(evidenceId: string) {
  return useQuery({
    queryKey: ['evidence', evidenceId, 'traceability'],
    queryFn: async () => {
      const { data } = await apiGet<{ steps: TraceabilityStep[] }>('/evidence/traceability', { evidenceId })
      return data
    },
    enabled: !!evidenceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}
