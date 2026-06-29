import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { InteractionType, InteractionStatus, Interaction } from '@/types/interactions'

export interface UseInteractionsParams {
  type?: InteractionType
  status?: InteractionStatus
  search?: string
  customerId?: string
  page?: number
  limit?: number
}

export interface UseInteractionsTimelineParams {
  customerId?: string
  type?: InteractionType
}

export function useInteractions(params: UseInteractionsParams) {
  return useQuery({
    queryKey: ['interactions', params],
    queryFn: async () => {
      const { data } = await apiGet<{ items: Interaction[]; total: number }>('/interactions', {
        type: params.type,
        status: params.status,
        search: params.search,
        customer_id: params.customerId,
        page: params.page,
        limit: params.limit,
      })
      return data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30_000,
    retry: 2,
  })
}

export function useInteractionById(id: string) {
  return useQuery({
    queryKey: ['interaction', id],
    queryFn: async () => {
      const { data } = await apiGet<Interaction>(`/interactions/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useInteractionsTimeline(params: UseInteractionsTimelineParams) {
  return useQuery({
    queryKey: ['interactions', 'timeline', params],
    queryFn: async () => {
      const { data } = await apiGet<{ groups: { date: string; interactions: Interaction[] }[] }>(
        '/interactions/timeline',
        { customer_id: params.customerId, type: params.type },
      )
      return data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}
