import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'

interface PluginsResponse {
  plugins: unknown[]
  total: number
}

interface RegistryResponse {
  results: unknown[]
  total: number
  query: string
}

export function usePluginsList() {
  return useQuery({
    queryKey: ['plugins'],
    queryFn: async () => {
      const { data } = await apiGet<PluginsResponse>('/plugins')
      return data?.plugins ?? []
    },
    staleTime: 60_000,
    retry: 2,
  })
}

export function usePluginById(id: string) {
  return useQuery({
    queryKey: ['plugins', id],
    queryFn: async () => {
      const { data } = await apiGet(`/plugins/${id}`)
      return data
    },
    enabled: !!id,
    retry: 2,
  })
}

export function useRegistrySearch(search: string) {
  return useQuery({
    queryKey: ['registry', 'search', search],
    queryFn: async () => {
      const { data } = await apiGet<RegistryResponse>('/registry/search', { q: search })
      return data?.results ?? []
    },
    enabled: search.length > 0,
    staleTime: 60_000,
    retry: 2,
  })
}
