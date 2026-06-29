import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost } from '@/api/client'
import type { CopilotSuggestion } from '@/types/copilot'

interface ChatResponse {
  response: string
  conversation_id: string
}

export function useCopilotSuggestions() {
  return useQuery({
    queryKey: ['copilot', 'suggestions'],
    queryFn: async () => {
      const { data } = await apiGet<{ questions: CopilotSuggestion[] }>('/llm/suggestions')
      return data?.questions ?? []
    },
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useSendCopilotMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ message, conversationId }: { message: string; conversationId?: string | null }) => {
      const { data } = await apiPost<ChatResponse>('/llm/chat', {
        message,
        conversation_id: conversationId,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copilot'] })
    },
  })
}
