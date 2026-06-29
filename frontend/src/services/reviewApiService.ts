import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPost } from '@/api/client'
import type { ReviewItem, ReviewSummary } from '@/types/review'

interface ReviewListResponse {
  reviews?: ReviewItem[]
  total?: number
}

export interface UseReviewParams {
  status?: string
  priority?: string
  search?: string
  page?: number
  limit?: number
}

export function useReviewList(params: UseReviewParams) {
  return useQuery({
    queryKey: ['reviews', params],
    queryFn: async () => {
      const { data } = await apiGet<ReviewListResponse>('/decision-review/reviews', {
        status: params.status,
        priority: params.priority,
        q: params.search ?? '',
        page: params.page ?? 1,
        limit: params.limit ?? 12,
      })
      const items = data?.reviews ?? []
      return { items, total: data?.total ?? items.length }
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useReviewById(id: string) {
  return useQuery({
    queryKey: ['reviews', id],
    queryFn: async () => {
      const { data } = await apiGet<ReviewItem>(`/decision-review/reviews/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useReviewSummary() {
  return useQuery({
    queryKey: ['reviews', 'summary'],
    queryFn: async () => {
      const { data } = await apiGet<ReviewListResponse>('/decision-review/reviews', { limit: 100 })
      const items = data?.reviews ?? []
      return {
        pending: items.filter((r) => r.status === 'pending').length,
        underReview: items.filter((r) => r.status === 'under_review').length,
        moreInfoNeeded: items.filter((r) => r.status === 'more_info_needed').length,
        approved: items.filter((r) => r.status === 'approved').length,
        rejected: items.filter((r) => r.status === 'rejected').length,
        scheduled: items.filter((r) => r.status === 'scheduled').length,
        total: items.length,
      } as ReviewSummary
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useApproveReview() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, comment }: { reviewId: string; comment?: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/approve`, { comment })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useRejectReview() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, reason }: { reviewId: string; reason?: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/reject`, { reason })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useRequestInfo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, question }: { reviewId: string; question?: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/request-info`, { question })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useAddComment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, text, author }: { reviewId: string; text: string; author?: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/comments`, { text, author })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useAssignEngineer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, engineer }: { reviewId: string; engineer: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/assign`, { engineer })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useScheduleAction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ reviewId, scheduledDate, notes }: { reviewId: string; scheduledDate: string; notes?: string }) => {
      const { data } = await apiPost<ReviewItem>(`/decision-review/reviews/${reviewId}/schedule`, { scheduled_date: scheduledDate, notes })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}
