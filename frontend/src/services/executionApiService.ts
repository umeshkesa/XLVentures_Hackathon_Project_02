import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { ExecutionItem, ExecutionSummary } from '@/types/execution'

interface ExecutionListResponse {
  actions?: ExecutionItem[]
  total?: number
}

export interface UseExecutionParams {
  status?: string
  priority?: string
  search?: string
  page?: number
  limit?: number
}

export function useExecutionList(params: UseExecutionParams) {
  return useQuery({
    queryKey: ['executions', params],
    queryFn: async () => {
      const { data } = await apiGet<ExecutionListResponse>('/action-manager/actions', {
        status: params.status,
        priority: params.priority,
        q: params.search ?? '',
        page: params.page ?? 1,
        limit: params.limit ?? 12,
      })
      const items = data?.actions ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useExecutionById(id: string) {
  return useQuery({
    queryKey: ['executions', id],
    queryFn: async () => {
      const { data } = await apiGet<ExecutionItem>(`/action-manager/actions/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useExecutionSummary() {
  return useQuery({
    queryKey: ['executions', 'summary'],
    queryFn: async () => {
      const { data } = await apiGet<ExecutionListResponse>('/action-manager/actions', { limit: 100 })
      const items = data?.actions ?? []
      return {
        pending: items.filter((a) => a.status === 'pending').length,
        inProgress: items.filter((a) => a.status === 'in_progress').length,
        completed: items.filter((a) => a.status === 'completed').length,
        cancelled: items.filter((a) => a.status === 'cancelled').length,
        total: items.length,
      } as ExecutionSummary
    },
    staleTime: 30_000,
    retry: 2,
  })
}
