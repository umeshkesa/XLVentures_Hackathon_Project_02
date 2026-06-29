import apiClient from '@/api/client'
import type { ImportResult, ImportHistory, ImportReport } from '@/types/import'

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
      const { data } = await apiClient.post<ImportResult>('/import/upload', form)
      return data
    },
    async uploadZip(file: File): Promise<ImportResult> {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post<ImportResult>('/import/zip', form)
      return data
    },
    async uploadCsv(file: File): Promise<ImportResult> {
      const form = new FormData()
      form.append('file', file)
      const { data } = await apiClient.post<ImportResult>('/import/csv', form)
      return data
    },
    async getStatus(jobId: string): Promise<ImportResult> {
      const { data } = await apiClient.get<ImportResult>(`/import/status/${jobId}`)
      return data
    },
    async getHistory(limit = 50, offset = 0): Promise<ImportHistory> {
      const { data } = await apiClient.get<ImportHistory>('/import/history', { params: { limit, offset } })
      return data
    },
    async getReport(jobId: string): Promise<ImportReport> {
      const { data } = await apiClient.get<ImportReport>(`/import/report/${jobId}`)
      return data
    },
  }
}
