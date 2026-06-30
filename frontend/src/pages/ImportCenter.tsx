import { useState, useCallback, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload,
  FileText,
  FileJson,
  File as FileIcon,
  Archive,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  Loader2,
  ChevronRight,
  History,
  Download,
  Trash2,
  Search,
  Tag,
  Database,
  BookOpen,
  Scale,
  ClipboardList,
  BrainCircuit,
  ThumbsUp,
  GitMerge,
  Eye,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/Table'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { cn } from '@/lib/utils'
import { useImportService } from '@/services/importService'
import type {
  ImportJobSummary, ClassificationResult, PipelineStage, RecommendationDetail,
} from '@/types/import'
import { triggerDashboardRefresh } from '@/utils/refreshDashboard'

type View = 'upload' | 'history'

const fileTypeIcons: Record<string, LucideIcon> = {
  '.csv': FileText,
  '.json': FileJson,
  '.txt': FileIcon,
  '.pdf': FileIcon,
  '.zip': Archive,
}

const fileTypeColors: Record<string, string> = {
  '.csv': 'text-emerald-500 bg-emerald-500/10',
  '.json': 'text-blue-500 bg-blue-500/10',
  '.txt': 'text-slate-500 bg-slate-500/10',
  '.pdf': 'text-red-500 bg-red-500/10',
  '.zip': 'text-amber-500 bg-amber-500/10',
}

interface UploadResult {
  jobId: string
  classification?: ClassificationResult | ClassificationResult[]
  summary?: Record<string, unknown>
  recommendations?: Record<string, unknown>
  pipelineStages?: PipelineStage[]
  error?: string
}

const PIPELINE_STAGES_CONFIG = [
  { name: 'upload', label: 'Uploading', icon: Upload, color: 'slate' },
  { name: 'classification', label: 'Content Classification', icon: Tag, color: 'blue' },
  { name: 'entity_extraction', label: 'Entity Extraction', icon: Search, color: 'cyan' },
  { name: 'evidence_generation', label: 'Evidence Generation', icon: Database, color: 'purple' },
  { name: 'knowledge_retrieval', label: 'Knowledge Retrieval', icon: BookOpen, color: 'yellow' },
  { name: 'rule_evaluation', label: 'Business Rule Evaluation', icon: Scale, color: 'orange' },
  { name: 'planner_agent', label: 'Planner Agent', icon: ClipboardList, color: 'indigo' },
  { name: 'reasoning_agent', label: 'Reasoning Agent', icon: BrainCircuit, color: 'violet' },
  { name: 'recommendation_agent', label: 'Recommendation Agent', icon: ThumbsUp, color: 'emerald' },
  { name: 'explainability', label: 'Explainability', icon: GitMerge, color: 'teal' },
  { name: 'human_review', label: 'Human Review', icon: Eye, color: 'amber' },
  { name: 'completed', label: 'Completed', icon: CheckCircle2, color: 'emerald' },
]

const STAGE_BG_COLORS: Record<string, string> = {
  slate: 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700',
  blue: 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800',
  cyan: 'bg-cyan-50 dark:bg-cyan-950 border-cyan-200 dark:border-cyan-800',
  purple: 'bg-purple-50 dark:bg-purple-950 border-purple-200 dark:border-purple-800',
  yellow: 'bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800',
  orange: 'bg-orange-50 dark:bg-orange-950 border-orange-200 dark:border-orange-800',
  indigo: 'bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800',
  violet: 'bg-violet-50 dark:bg-violet-950 border-violet-200 dark:border-violet-800',
  emerald: 'bg-emerald-50 dark:bg-emerald-950 border-emerald-200 dark:border-emerald-800',
  teal: 'bg-teal-50 dark:bg-teal-950 border-teal-200 dark:border-teal-800',
  amber: 'bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800',
}

export default function ImportCenter() {
  const [view, setView] = useState<View>('upload')
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Import Center</h1>
        <p className="text-muted-foreground">Upload and manage data imports with full enterprise pipeline visibility</p>
      </div>

      <div className="flex gap-1 rounded-lg border p-1 w-fit bg-muted/50">
        <button onClick={() => setView('upload')} className={cn(
          'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
          view === 'upload' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground',
        )}>
          <Upload className="h-4 w-4" />
          Upload
        </button>
        <button onClick={() => setView('history')} className={cn(
          'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
          view === 'history' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground',
        )}>
          <History className="h-4 w-4" />
          Import History
        </button>
      </div>

      {view === 'upload' ? <UploadView /> : <ImportHistoryView />}
    </div>
  )
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}

function PipelineVisualizer({ stages }: { stages: PipelineStage[] }) {
  const activeIndex = stages.findIndex(
    (s) => s.status === 'in_progress' || s.status === 'pending'
  )

  return (
    <div className="space-y-0">
      {PIPELINE_STAGES_CONFIG.map((cfg, idx) => {
        const stage = stages.find((s) => s.name === cfg.name)
        const status = stage?.status ?? 'pending'
        const isCompleted = status === 'completed'
        const isActive = status === 'in_progress'
        const isFailed = status === 'failed'
        const isPending = status === 'pending'
        const isLast = idx === PIPELINE_STAGES_CONFIG.length - 1
        const isPast = activeIndex > idx

        const StageIcon = cfg.icon

        return (
          <div key={cfg.name} className="flex gap-4">
            {/* Left side: connector + status icon */}
            <div className="flex flex-col items-center">
              <div className={cn(
                'flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 transition-all',
                isCompleted && 'bg-emerald-500 border-emerald-500 text-white',
                isActive && 'bg-blue-500 border-blue-500 text-white shadow-lg shadow-blue-500/30 scale-110',
                isFailed && 'bg-red-500 border-red-500 text-white',
                isPending && 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-slate-400',
                isPast && 'opacity-60',
              )}>
                {isCompleted && <CheckCircle2 className="h-5 w-5" />}
                {isActive && <Loader2 className="h-5 w-5 animate-spin" />}
                {isFailed && <XCircle className="h-5 w-5" />}
                {isPending && <StageIcon className="h-5 w-5" />}
              </div>
              {!isLast && (
                <div className={cn(
                  'w-0.5 h-8',
                  isCompleted ? 'bg-emerald-400' : 'bg-slate-200 dark:bg-slate-700',
                )} />
              )}
            </div>

            {/* Right side: stage content */}
            <div className={cn(
              'flex-1 rounded-lg border p-4 mb-2 transition-all',
              isActive && STAGE_BG_COLORS[cfg.color],
              isCompleted && 'bg-slate-50 dark:bg-slate-800/50',
              isFailed && 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800',
              isPending && 'bg-white dark:bg-slate-800',
              isPast && 'opacity-60',
            )}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'text-sm font-semibold',
                    isActive && 'text-blue-700 dark:text-blue-300',
                    isCompleted && 'text-emerald-700 dark:text-emerald-300',
                    isFailed && 'text-red-700 dark:text-red-300',
                    isPending && 'text-slate-600 dark:text-slate-400',
                  )}>
                    {cfg.label}
                  </span>
                  <span className={cn(
                    'text-[10px] px-2 py-0.5 rounded-full font-medium',
                    isCompleted && 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
                    isActive && 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 animate-pulse',
                    isFailed && 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
                    isPending && 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400',
                  )}>
                    {isCompleted && 'Success'}
                    {isActive && 'Running...'}
                    {isFailed && 'Failed'}
                    {isPending && 'Pending'}
                  </span>
                </div>
                {stage?.durationMs && stage.durationMs > 0 && (
                  <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">
                    {stage.durationMs}ms
                  </span>
                )}
              </div>

              {stage?.startedAt && (
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 font-mono">
                  {new Date(stage.startedAt).toLocaleTimeString()}
                  {stage.completedAt && ` → ${new Date(stage.completedAt).toLocaleTimeString()}`}
                </p>
              )}

              {stage?.error && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">{stage.error}</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function UploadView() {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>([])
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const svc = useImportService()
  const navigate = useNavigate()

  const supportedExtensions = ['.csv', '.json', '.txt', '.pdf', '.zip']

  const isValidFile = (f: File) => {
    const ext = '.' + f.name.split('.').pop()?.toLowerCase()
    return supportedExtensions.includes(ext)
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && isValidFile(f)) {
      setFile(f)
      setResult(null)
      setError(null)
    } else {
      setError('Unsupported file type. Supported: CSV, JSON, TXT, PDF, ZIP')
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)
    setResult(null)

    const initialStages: PipelineStage[] = PIPELINE_STAGES_CONFIG.map((cfg) => ({
      name: cfg.name,
      label: cfg.label,
      status: 'pending',
      startedAt: null,
      completedAt: null,
      durationMs: 0,
      error: null,
    }))

    initialStages[0] = { ...initialStages[0], status: 'in_progress', startedAt: new Date().toISOString() }
    setPipelineStages(initialStages)

    try {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase()
      let response
      if (ext === '.zip') {
        response = await svc.uploadZip(file)
      } else if (ext === '.csv') {
        response = await svc.uploadCsv(file)
      } else {
        response = await svc.upload(file)
      }

      if (response.status === 'failed') {
        const errMsg = response.summary && 'error' in response.summary
          ? (response.summary as Record<string, string>).error ?? 'Upload failed'
          : 'Upload failed'
        setError(errMsg)
        setUploading(false)
        return
      }

      const pollInterval = 800
      let jobStatus: string = response.status
      while (jobStatus === 'pending' || jobStatus === 'processing' || jobStatus === 'extracting') {
        await sleep(pollInterval)
        const statusResp = await svc.getStatus(response.jobId)
        jobStatus = statusResp.status
      }

      const report = await svc.getReport(response.jobId)
      const classification = report.classification
      const summary = report.importSummary ?? {}
      const recs = report.recommendations ?? {}
      const stages = report.pipelineStages ?? []

      if (stages.length > 0) {
        setPipelineStages(stages)
      } else {
        setPipelineStages(
          initialStages.map((s) => ({ ...s, status: 'completed' as const }))
        )
      }

      setResult({
        jobId: response.jobId,
        classification,
        summary,
        recommendations: recs,
        pipelineStages: stages,
      })

      setUploading(false)
      triggerDashboardRefresh()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed'
      setError(msg)
      setUploading(false)
      setPipelineStages((prev) =>
        prev.map((s) =>
          s.status === 'in_progress'
            ? { ...s, status: 'failed' as const, error: msg, completedAt: new Date().toISOString() }
            : s
        )
      )
    }
  }

  const fileExt = file ? '.' + file.name.split('.').pop()?.toLowerCase() : ''
  const IconComponent = fileTypeIcons[fileExt] ?? FileIcon

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <Card className="lg:col-span-3">
        <CardHeader>
          <CardTitle>Upload Files</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {!uploading && !result ? (
            <>
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
                className={cn(
                  'flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors',
                  isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-muted-foreground/50',
                )}
              >
                <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-lg font-medium">Drop files here</p>
                <p className="mt-1 text-sm text-muted-foreground">or click to browse</p>
                <p className="mt-3 text-xs text-muted-foreground">Supports CSV, JSON, TXT, PDF, and ZIP archives</p>
                <input ref={inputRef} type="file" className="hidden" onChange={handleFileSelect} accept=".csv,.json,.txt,.pdf,.zip" />
              </div>

              {file && (
                <div className="flex items-center gap-4 rounded-lg border p-4">
                  <div className={cn('rounded-lg p-2.5', fileTypeColors[fileExt] ?? 'bg-muted text-muted-foreground')}>
                    <IconComponent className="h-6 w-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setFile(null)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}

              {error && (
                <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-600 dark:text-red-400">
                  <AlertCircle className="h-5 w-5 shrink-0" />
                  {error}
                </div>
              )}

              <Button onClick={handleUpload} disabled={!file || uploading} className="w-full" size="lg">
                {uploading ? <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</> : <><Upload className="h-4 w-4" /> Upload & Import</>}
              </Button>
            </>
          ) : null}

          {(uploading || result) && pipelineStages.length > 0 && (
            <PipelineVisualizer stages={pipelineStages} />
          )}

          {result && !uploading && (
            <div className="space-y-6">
              {result.error ? (
                <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-600 dark:text-red-400">
                  <XCircle className="h-5 w-5 shrink-0" />
                  {result.error}
                </div>
              ) : (
                <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                    <div>
                      <p className="font-medium text-emerald-600 dark:text-emerald-400">Import completed successfully</p>
                      <p className="text-sm text-muted-foreground">Job ID: {result.jobId}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Classification Display */}
              {result.classification && (
                <ClassificationDisplay
                  classification={result.classification}
                />
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <StatBox
                  value={((result.summary as Record<string, unknown>)?.importedCount as number) ??
                   ((result.summary as Record<string, unknown>)?.rowsImported as number) ??
                   ((result.summary as Record<string, unknown>)?.totalImported as number) ??
                   ((result.summary as Record<string, unknown>)?.evidenceGenerated as number) ?? 0}
                  label="Records Imported"
                />
                <StatBox
                  value={(result.summary as Record<string, unknown>)?.evidenceGenerated as number ?? 0}
                  label="Evidence Created"
                />
                <StatBox
                  value={(result.recommendations as Record<string, unknown>)?.nextBestAction ? 'Yes' : '—'}
                  label="Recommendations"
                />
                <StatBox
                  value={(result.recommendations as Record<string, unknown>)?.reasoning ? 'Yes' : '—'}
                  label="Reasoning Triggered"
                />
              </div>

              <RecommendationCard
                detail={(result.recommendations as Record<string, unknown>)?.recommendationDetails as RecommendationDetail | undefined}
                summaryRecommendation={
                  (result.summary as Record<string, unknown>)?.recommendation as string ?? ''
                }
                summaryConfidence={
                  (result.summary as Record<string, unknown>)?.confidence as number ?? 0
                }
                summaryReasoning={
                  (result.summary as Record<string, unknown>)?.reasoning as string ?? ''
                }
                summaryEvidenceIds={
                  (result.summary as Record<string, unknown>)?.evidenceIds as string[] ?? []
                }
                summaryKnowledgeIds={
                  (result.summary as Record<string, unknown>)?.knowledgeIds as string[] ?? []
                }
                summaryRuleIds={
                  (result.summary as Record<string, unknown>)?.ruleIds as string[] ?? []
                }
                summaryIssue={
                  (result.summary as Record<string, unknown>)?.issue as string ?? ''
                }
                summarySeverity={
                  (result.summary as Record<string, unknown>)?.severity as string ?? ''
                }
              />

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button onClick={() => { setFile(null); setResult(null); setPipelineStages([]) }}>
                  <Upload className="h-4 w-4" /> Import Another
                </Button>
                <Button variant="outline" onClick={() => navigate(`/import/report/${result.jobId}`)}>
                  View Full Report <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sidebar: supported formats */}
      <Card className="lg:col-span-2">
        <CardHeader><CardTitle>Supported Formats</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {[
            { ext: '.csv', icon: FileText, label: 'CSV Files', desc: 'Customer data, incidents, sensor readings' },
            { ext: '.json', icon: FileJson, label: 'JSON Files', desc: 'Rules, configurations, recommendations' },
            { ext: '.txt', icon: FileIcon, label: 'Text Files', desc: 'Knowledge articles, playbooks, SOPs' },
            { ext: '.pdf', icon: FileIcon, label: 'PDF Documents', desc: 'Manuals, reports, compliance docs' },
            { ext: '.zip', icon: Archive, label: 'ZIP Archives', desc: 'Batch upload of multiple files' },
          ].map(({ ext, icon: Icon, label, desc }) => (
            <div key={ext} className="flex items-start gap-3">
              <div className={cn('rounded-lg p-2', fileTypeColors[ext] ?? 'bg-muted text-muted-foreground')}>
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-medium">{label}</p>
                <p className="text-xs text-muted-foreground">{desc}</p>
              </div>
            </div>
          ))}

          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-semibold mb-2">Enterprise Pipeline</h4>
            <p className="text-xs text-muted-foreground">
              Each uploaded file passes through a 12-stage enterprise pipeline for classification,
              entity extraction, evidence generation, knowledge retrieval, rule evaluation,
              planning, reasoning, recommendation, explainability, and human review.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ClassificationDisplay({
  classification,
}: {
  classification: ClassificationResult | ClassificationResult[]
}) {
  const items = Array.isArray(classification) ? classification : [classification]
  return (
    <div>
      <p className="mb-2 text-sm font-medium">Classification Results</p>
      <div className="rounded-lg border">
        {items.map((c, i) => (
          <div key={i} className="flex flex-col border-b last:border-b-0 px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground">{c.category}</p>
                <p className="text-xs text-muted-foreground">{c.sourceName} · detected by: {c.detectedBy}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={(c.confidence >= 0.8 ? 'success' : c.confidence >= 0.5 ? 'warning' : 'secondary') as 'success' | 'warning' | 'secondary'}>
                  {(c.confidence * 100).toFixed(0)}%
                </Badge>
                <Badge>{c.targetModules?.[0]}</Badge>
              </div>
            </div>
            {(c as any).classificationReason && (
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Reason:</span>
                <span className="text-xs text-slate-700 dark:text-slate-300 italic">
                  {(c as any).classificationReason}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function StatBox({ value, label }: { value: number | string; label: string }) {
  return (
    <div className="rounded-lg border p-3 text-center">
      <p className="text-2xl font-bold">{String(value)}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}

function RecommendationCard({
  detail,
  summaryRecommendation,
  summaryConfidence,
  summaryReasoning,
  summaryEvidenceIds,
  summaryKnowledgeIds,
  summaryRuleIds,
  summaryIssue,
  summarySeverity,
}: {
  detail: RecommendationDetail | undefined
  summaryRecommendation: string
  summaryConfidence: number
  summaryReasoning: string
  summaryEvidenceIds: string[]
  summaryKnowledgeIds: string[]
  summaryRuleIds: string[]
  summaryIssue: string
  summarySeverity: string
}) {
  const hasData = detail || summaryRecommendation

  if (!hasData) return null

  const issue = summaryIssue || detail?.issue || 'Data Analysis'
  const severity = summarySeverity || detail?.severity || 'medium'
  const recommendation = summaryRecommendation || detail?.recommendation || detail?.conclusion || detail?.primaryRecommendation || '—'
  const confidence = summaryConfidence || detail?.confidenceScore || detail?.confidence || 0
  const reasoning = summaryReasoning || detail?.reasoning || detail?.reasoningSummary || ''
  const evidence = summaryEvidenceIds?.length > 0 ? summaryEvidenceIds : (detail?.evidence ?? [])
  const knowledge = summaryKnowledgeIds?.length > 0 ? summaryKnowledgeIds : (detail?.knowledge ?? [])
  const rules = summaryRuleIds?.length > 0 ? summaryRuleIds : (detail?.rules ?? [])

  const severityColor = severity === 'critical' ? 'red' : severity === 'high' ? 'orange' : severity === 'medium' ? 'yellow' : 'slate'

  return (
    <div>
      <p className="mb-3 text-sm font-medium">Recommendation Details</p>
      <div className="space-y-3">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Issue</p>
                <p className="font-semibold text-foreground">{issue}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Severity</p>
                <Badge variant={(severityColor === 'red' ? 'destructive' : severityColor === 'orange' ? 'warning' : 'secondary') as 'destructive' | 'warning' | 'secondary'}>
                  {severity}
                </Badge>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Recommendation</p>
                <p className="font-medium text-foreground">{recommendation}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Confidence</p>
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                    <div
                      className={cn(
                        'h-full rounded-full transition-all',
                        confidence >= 0.7 ? 'bg-emerald-500' : confidence >= 0.4 ? 'bg-amber-500' : 'bg-red-500',
                      )}
                      style={{ width: `${confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold">{(confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {reasoning && (
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-1">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Reasoning</p>
                <p className="text-sm text-foreground">{reasoning}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Evidence, Knowledge, Rules */}
        <div className="grid gap-3 sm:grid-cols-3">
          {evidence.length > 0 && (
            <Card>
              <CardContent className="pt-4">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Evidence Used</p>
                <div className="space-y-1">
                  {evidence.map((id: string) => (
                    <div key={id} className="flex items-center gap-1.5 text-xs">
                      <Database className="h-3 w-3 text-purple-500 shrink-0" />
                      <span className="text-foreground">{id}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {knowledge.length > 0 && (
            <Card>
              <CardContent className="pt-4">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Knowledge Retrieved</p>
                <div className="space-y-1">
                  {knowledge.map((id: string) => (
                    <div key={id} className="flex items-center gap-1.5 text-xs">
                      <BookOpen className="h-3 w-3 text-yellow-500 shrink-0" />
                      <span className="text-foreground">{id}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {rules.length > 0 && (
            <Card>
              <CardContent className="pt-4">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Rules Triggered</p>
                <div className="space-y-1">
                  {rules.map((id: string) => (
                    <div key={id} className="flex items-center gap-1.5 text-xs">
                      <Scale className="h-3 w-3 text-orange-500 shrink-0" />
                      <span className="text-foreground">{id}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Explainability */}
        {detail?.explainability && (
          <Card>
            <CardContent className="pt-4">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Alternative Actions Considered</p>
              <div className="space-y-2">
                {detail.explainability.alternativeActions.map((alt, i) => (
                  <div key={i} className="flex items-center justify-between text-xs p-2 bg-muted/50 rounded-lg">
                    <span className="text-foreground">{alt.title}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{(alt.confidence * 100).toFixed(0)}%</span>
                      <span className="text-muted-foreground text-[10px] italic">{alt.reason}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

function ImportHistoryView() {
  const svc = useImportService()
  const [jobs, setJobs] = useState<ImportJobSummary[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const limit = 20
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    svc.getHistory(limit, page * limit).then((res) => {
      setJobs(res.jobs)
      setTotal(res.total)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load history')
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const statusIcon: Record<string, LucideIcon> = {
    completed: CheckCircle2,
    failed: XCircle,
    processing: Loader2,
    pending: Clock,
  }
  const statusColor: Record<string, string> = {
    completed: 'text-emerald-500',
    failed: 'text-red-500',
    processing: 'text-blue-500',
    pending: 'text-amber-500',
    extracting: 'text-blue-500',
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Import History</CardTitle>
        <Button variant="outline" size="sm" onClick={load}><Download className="h-4 w-4" /> Refresh</Button>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="flex justify-center py-16"><LoadingSpinner label="Loading history..." /></div>
        ) : error ? (
          <div className="p-6"><ErrorState message={error} onRetry={load} /></div>
        ) : jobs.length === 0 ? (
          <div className="p-6"><EmptyState title="No imports yet" description="Upload your first file to get started." /></div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => {
                  const Icon = fileTypeIcons[job.fileType] ?? FileIcon
                  const StatusIcon = statusIcon[job.status] ?? Clock
                  return (
                    <TableRow key={job.jobId}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className={cn('rounded-lg p-2', fileTypeColors[job.fileType] ?? 'bg-muted')}>
                            <Icon className="h-4 w-4" />
                          </div>
                          <span className="font-medium">{job.filename}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm uppercase">{job.fileType.replace('.', '')}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{new Date(job.createdAt).toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-20 overflow-hidden rounded-full bg-muted">
                            <div className={cn(
                              'h-full rounded-full transition-all',
                              job.status === 'completed' ? 'bg-emerald-500' : job.status === 'failed' ? 'bg-red-500' : 'bg-blue-500',
                            )} style={{ width: `${job.progress}%` }} />
                          </div>
                          <span className="text-xs text-muted-foreground">{job.progress}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5">
                          <StatusIcon className={cn('h-4 w-4', statusColor[job.status] ?? 'text-muted-foreground')} />
                          <span className="text-sm capitalize">{job.status}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/import/report/${job.jobId}`)}>
                          Report
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
            <div className="flex items-center justify-between border-t px-6 py-4">
              <p className="text-sm text-muted-foreground">
                Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={page <= 0} onClick={() => setPage(page - 1)}>Prev</Button>
                <Button variant="outline" size="sm" disabled={(page + 1) * limit >= total} onClick={() => setPage(page + 1)}>Next</Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
