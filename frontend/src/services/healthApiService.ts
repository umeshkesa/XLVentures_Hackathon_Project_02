import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'

interface HealthResponse {
  status: string
  version: string
  uptime_seconds: number
}

interface ReadyResponse {
  ready: boolean
  version: string
}

interface LiveResponse {
  alive: boolean
}

interface VersionResponse {
  version: string
}

interface ImportHistoryResponse {
  jobs: Array<{
    job_id: string
    status: string
    file_name: string
    created_at: string
  }>
  total: number
}

export function useApiHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await apiGet<HealthResponse>('/health')
      return data
    },
    staleTime: 10_000,
    refetchInterval: 15_000,
    retry: 2,
  })
}

export function useApiReady() {
  return useQuery({
    queryKey: ['health', 'ready'],
    queryFn: async () => {
      const { data } = await apiGet<ReadyResponse>('/ready')
      return data
    },
    staleTime: 10_000,
    refetchInterval: 15_000,
    retry: 2,
  })
}

export function useApiLive() {
  return useQuery({
    queryKey: ['health', 'live'],
    queryFn: async () => {
      const { data } = await apiGet<LiveResponse>('/live')
      return data
    },
    staleTime: 10_000,
    refetchInterval: 15_000,
    retry: 2,
  })
}

export function useApiVersion() {
  return useQuery({
    queryKey: ['health', 'version'],
    queryFn: async () => {
      const { data } = await apiGet<VersionResponse>('/version')
      return data
    },
    staleTime: 300_000,
    retry: 2,
  })
}

export function useImportJobs() {
  return useQuery({
    queryKey: ['health', 'imports'],
    queryFn: async () => {
      const { data } = await apiGet<ImportHistoryResponse>('/import/history', { limit: 50, offset: 0 })
      return data?.jobs ?? []
    },
    staleTime: 30_000,
    refetchInterval: 30_000,
    retry: 2,
  })
}
