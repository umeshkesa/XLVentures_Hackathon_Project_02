export interface ServiceHealth {
  name: string
  status: 'healthy' | 'degraded' | 'down' | 'unknown'
  latency: number
  uptime: number
  details?: string
}

export interface SystemMetrics {
  memoryUsage: number
  cpuUsage: number
  requestRate: number
  errorRate: number
  activeUsers: number
  totalRequests: number
}

export interface ImportQueueItem {
  id: string
  fileName: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  createdAt: string
}

export interface BackgroundJob {
  id: string
  name: string
  status: 'running' | 'completed' | 'failed' | 'scheduled'
  progress: number
  startedAt: string
  estimatedCompletion: string
}
