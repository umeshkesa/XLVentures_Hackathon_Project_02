import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { KnowledgeCategory, DocumentStatus, KnowledgeDocument } from '@/types/knowledge'

interface KnowledgeQueryResponse {
  items?: KnowledgeDocument[]
  results?: KnowledgeDocument[]
  total?: number
}

export interface UseKnowledgeParams {
  category?: KnowledgeCategory
  status?: DocumentStatus
  search?: string
  page?: number
  limit?: number
}

export function useKnowledge(params: UseKnowledgeParams) {
  return useQuery({
    queryKey: ['knowledge', params],
    queryFn: async () => {
      const { data } = await apiGet<KnowledgeQueryResponse>('/knowledge/query', {
        q: params.search ?? '',
        category: params.category,
        status: params.status,
        page: params.page,
        limit: params.limit,
      })
      const items = data?.items ?? data?.results ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 60_000,
    retry: 2,
  })
}

export function useKnowledgeById(id: string) {
  return useQuery({
    queryKey: ['knowledge', id],
    queryFn: async () => {
      const { data } = await apiGet<KnowledgeDocument>(`/knowledge/documents/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}
