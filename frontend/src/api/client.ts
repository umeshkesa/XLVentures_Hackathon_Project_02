import axios from 'axios'
import type { ApiResponse } from '@/types/api'
import { toast } from 'sonner'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isCancel(error)) return Promise.reject(error)

    const message =
      error.response?.data?.error?.message ??
      error.message ??
      'An unexpected error occurred'

    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }
      if (status >= 500) {
        toast.error('Server error', { description: message })
      }
    } else if (error.request) {
      toast.error('Network error', {
        description: 'Unable to reach the server. Please check your connection.',
      })
    }

    return Promise.reject(error)
  },
)

export async function apiGet<T>(
  url: string,
  params?: Record<string, unknown>,
): Promise<ApiResponse<T>> {
  const { data } = await apiClient.get(url, { params })
  // Some backend endpoints (health, ready, live, version, import/history)
  // return raw models instead of ApiResponse-wrapped responses.
  // Normalize: if the response body has no "data" key, wrap it.
  if (data && typeof data === 'object' && 'data' in data) {
    return data as ApiResponse<T>
  }
  return { data } as unknown as ApiResponse<T>
}

export async function apiPost<T>(
  url: string,
  body?: unknown,
): Promise<ApiResponse<T>> {
  const { data } = await apiClient.post<ApiResponse<T>>(url, body)
  return data
}

export async function apiPut<T>(
  url: string,
  body?: unknown,
): Promise<ApiResponse<T>> {
  const { data } = await apiClient.put<ApiResponse<T>>(url, body)
  return data
}

export async function apiDelete<T>(url: string): Promise<ApiResponse<T>> {
  const { data } = await apiClient.delete<ApiResponse<T>>(url)
  return data
}

export default apiClient
