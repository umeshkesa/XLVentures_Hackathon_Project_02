import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'

interface HealthResponse {
  status: string
  version: string
  uptime_seconds: number
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['system', 'health'],
    queryFn: async () => {
      const { data } = await apiGet<HealthResponse>('/health')
      return data
    },
    staleTime: 15_000,
    refetchInterval: 30_000,
    retry: 2,
  })
}

export function useSystemReady() {
  return useQuery({
    queryKey: ['system', 'ready'],
    queryFn: async () => {
      const { data } = await apiGet<{ ready: boolean; version: string }>('/ready')
      return data
    },
    staleTime: 15_000,
    refetchInterval: 30_000,
    retry: 2,
  })
}
