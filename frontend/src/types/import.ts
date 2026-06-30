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
  classificationReason?: string
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
    pipelineStages?: PipelineStage[]
    recommendation?: string
    confidence?: number
    reasoning?: string
    evidenceIds?: string[]
    knowledgeIds?: string[]
    ruleIds?: string[]
    issue?: string
    severity?: string
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
  pipelineStages?: PipelineStage[]
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

export interface RecommendationDetail {
  conclusion: string
  confidence: number
  readiness: string
  primaryRecommendation: string
  reasoningSummary: string
  status: string
  issue?: string
  severity?: string
  recommendation?: string
  confidenceScore?: number
  reasoning?: string
  evidence?: string[]
  knowledge?: string[]
  rules?: string[]
  businessImpact?: string
  estimatedCost?: number
  estimatedSavings?: number
  timeline?: string
  explainability?: {
    evidenceUsed: string[]
    knowledgeRetrieved: string[]
    businessRulesTriggered: string[]
    reasoningSummary: string
    confidenceScore: number
    alternativeActions: { title: string; confidence: number; reason: string }[]
  }
}

export interface PipelinePhase {
  name: string
  label: string
  status: 'pending' | 'running' | 'completed' | 'skipped' | 'failed'
  detail?: string
  startedAt?: string
  completedAt?: string
  durationMs?: number
  error?: string
  description?: string
}

export interface PipelineStage {
  name: string
  label: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  startedAt: string | null
  completedAt: string | null
  durationMs: number
  error: string | null
  description?: string
}
