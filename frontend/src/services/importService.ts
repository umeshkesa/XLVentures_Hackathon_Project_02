import apiClient from '@/api/client'
import type { ImportResult, ImportHistory, ImportReport } from '@/types/import'

function snakeToCamel(value: unknown): unknown {
  if (value === null || value === undefined) return value
  if (Array.isArray(value)) return value.map(snakeToCamel)
  if (typeof value === 'object' && !(value instanceof Date)) {
    const obj = value as Record<string, unknown>
    const result: Record<string, unknown> = {}
    for (const key of Object.keys(obj)) {
      const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
      result[camelKey] = snakeToCamel(obj[key])
    }
    return result
  }
  return value
}

export interface ImportService {
  upload(file: File): Promise<ImportResult>
  uploadZip(file: File): Promise<ImportResult>
  uploadCsv(file: File): Promise<ImportResult>
  getStatus(jobId: string): Promise<ImportResult>
  getHistory(limit?: number, offset?: number): Promise<ImportHistory>
  getReport(jobId: string): Promise<ImportReport>
}

export function useImportService(): ImportService {
  return {
    async upload(file: File): Promise<ImportResult> {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post<ImportResult>('/import/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return snakeToCamel(data) as ImportResult
    },
    async uploadZip(file: File): Promise<ImportResult> {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post<ImportResult>('/import/zip', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return snakeToCamel(data) as ImportResult
    },
    async uploadCsv(file: File): Promise<ImportResult> {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post<ImportResult>('/import/csv', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return snakeToCamel(data) as ImportResult
    },
    async getStatus(jobId: string): Promise<ImportResult> {
      const { data } = await apiClient.get<ImportResult>(`/import/status/${jobId}`)
      return snakeToCamel(data) as ImportResult
    },
    async getHistory(limit = 50, offset = 0): Promise<ImportHistory> {
      const { data } = await apiClient.get<ImportHistory>('/import/history', { params: { limit, offset } })
      return snakeToCamel(data) as ImportHistory
    },
    async getReport(jobId: string): Promise<ImportReport> {
      const { data } = await apiClient.get<ImportReport>(`/import/report/${jobId}`)
      return snakeToCamel(data) as ImportReport
    },
  }
}
