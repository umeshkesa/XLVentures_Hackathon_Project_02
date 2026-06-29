export type ImportStatus = 'pending' | 'processing' | 'extracting' | 'completed' | 'failed'
export type FileType = '.csv' | '.json' | '.txt' | '.pdf' | '.zip'

export interface ImportJob {
  jobId: string
  filename: string
  fileType: FileType
  status: ImportStatus
  progress: number
  createdAt: string
  updatedAt: string
  completedAt?: string
  error?: string
}

export interface ImportJobSummary {
  jobId: string
  filename: string
  fileType: FileType
  status: ImportStatus
  progress: number
  createdAt: string
  completedAt?: string
}

export interface ClassificationResult {
  category: string
  confidence: number
  targetModules: string[]
  filePath: string
  sourceName: string
  detectedBy: string
  details?: Record<string, unknown>
}

export interface FileDetail {
  file: string
  category: string
  routedTo: string
  importedCount: number
}

export interface ImportResult {
  jobId: string
  status: ImportStatus
  progress: number
  summary?: {
    file?: string
    archive?: string
    classification: ClassificationResult | ClassificationResult[]
    routedTo?: string
    importedCount?: number
    totalImported?: number
    evidenceGenerated?: number
    reasoningTriggered?: boolean
    recommendationsGenerated?: boolean
    filesProcessed?: number
    fileDetails?: FileDetail[]
    rowsImported?: number
  }
}

export interface ImportReport {
  jobId: string
  filename: string
  fileType: FileType
  status: ImportStatus
  progress: number
  createdAt: string
  updatedAt: string
  completedAt?: string
  classification?: ClassificationResult | ClassificationResult[]
  importSummary?: Record<string, unknown>
  recommendations?: Record<string, unknown>
  error?: string
}

export interface ImportHistory {
  total: number
  offset: number
  limit: number
  jobs: ImportJobSummary[]
}

export interface UploadStage {
  label: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  detail?: string
}
