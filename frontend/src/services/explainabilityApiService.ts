import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { Explanation } from '@/types/explainability'

interface ExplainabilityListResponse {
  explanations?: Explanation[]
  total?: number
}

export function useExplanationList(page: number = 1, limit: number = 12) {
  return useQuery({
    queryKey: ['explanations', { page, limit }],
    queryFn: async () => {
      const { data } = await apiGet<ExplainabilityListResponse>('/explainability', { page, limit })
      const items = data?.explanations ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useExplanationById(id: string) {
  return useQuery({
    queryKey: ['explanations', id],
    queryFn: async () => {
      const { data } = await apiGet<Explanation>(`/explainability/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}
