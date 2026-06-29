import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost } from '@/api/client'
import type { SuggestedQuestion } from '@/types/llm'

interface ChatResponse {
  response: string
  conversation_id: string
}

interface SuggestionsResponse {
  questions: SuggestedQuestion[]
}

export function useSuggestedQuestions() {
  return useQuery({
    queryKey: ['llm', 'suggestions'],
    queryFn: async () => {
      const { data } = await apiGet<SuggestionsResponse>('/llm/suggestions')
      return data?.questions ?? []
    },
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      message,
      conversationId,
    }: {
      message: string
      conversationId?: string | null
    }) => {
      const { data } = await apiPost<ChatResponse>('/llm/chat', {
        message,
        conversation_id: conversationId,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['llm'] })
    },
  })
}
