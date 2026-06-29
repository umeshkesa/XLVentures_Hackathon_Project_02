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
import type { ImportJobSummary, FileDetail, ClassificationResult } from '@/types/import'
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

const stageLabels = ['Uploading', 'Classifying', 'Processing', 'Integrating', 'Generating']
const stageDurations = [800, 1200, 2000, 1500, 1000]

interface UploadResult {
  jobId: string
  classification?: ClassificationResult | ClassificationResult[]
  fileDetails?: FileDetail[]
  totalImported?: number
  evidenceGenerated?: number
  recommendationsGenerated?: boolean
  reasoningTriggered?: boolean
  error?: string
}

export default function ImportCenter() {
  const [view, setView] = useState<View>('upload')
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Import Center</h1>
        <p className="text-muted-foreground">Upload and manage data imports</p>
      </div>

      {/* View switcher */}
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

function UploadView() {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [stage, setStage] = useState(0)
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

  const runStages = async (jobId: string) => {
    for (let i = 0; i < stageLabels.length; i++) {
      setStage(i)
      await new Promise((r) => setTimeout(r, stageDurations[i]))
    }
    try {
      const report = await svc.getReport(jobId)
      setResult({
        jobId,
        classification: report.classification,
        totalImported: (report.importSummary as Record<string, number>)?.totalImported ?? (report.importSummary as Record<string, number>)?.importedCount ?? 0,
        evidenceGenerated: (report.importSummary as Record<string, number>)?.evidenceGenerated ?? 0,
        recommendationsGenerated: (report.recommendations as Record<string, boolean>) != null,
        reasoningTriggered: (report.importSummary as Record<string, boolean>)?.reasoningTriggered ?? false,
        error: report.error,
      })
      setStage(stageLabels.length)
    } catch {
      setResult({ jobId, error: 'Failed to fetch import report' })
    }
    triggerDashboardRefresh()
    setUploading(false)
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)
    setResult(null)
    setStage(0)

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
        setError(response.summary && 'error' in response.summary ? (response.summary as Record<string, string>).error ?? 'Upload failed' : 'Upload failed')
        setUploading(false)
        return
      }

      await runStages(response.jobId)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed'
      setError(msg)
      setUploading(false)
    }
  }

  const fileExt = file ? '.' + file.name.split('.').pop()?.toLowerCase() : ''
  const IconComponent = fileTypeIcons[fileExt] ?? FileIcon

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Upload card */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Upload Files</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {!uploading && !result ? (
            <>
              {/* Drag & drop zone */}
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

              {/* Selected file */}
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
                {uploading ? <><Loader2 className="h-4 w-4 animate-spin" /> Uploading...</> : <><Upload className="h-4 w-4" /> Upload & Import</>}
              </Button>
            </>
          ) : null}

          {/* Progress stepper */}
          {uploading && (
            <div className="space-y-6">
              <div className="space-y-4">
                {stageLabels.map((label, i) => {
                  const isActive = i === stage
                  const isDone = stage > i || (i === stageLabels.length - 1 && stage === stageLabels.length)
                  const isPending = i > stage
                  return (
                    <div key={label} className="flex items-center gap-3">
                      <div className={cn(
                        'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium',
                        isDone && 'bg-emerald-500 text-white',
                        isActive && 'bg-primary text-primary-foreground ring-2 ring-primary/30',
                        isPending && 'bg-muted text-muted-foreground',
                      )}>
                        {isDone ? <CheckCircle2 className="h-4 w-4" /> : isActive ? <Loader2 className="h-4 w-4 animate-spin" /> : i + 1}
                      </div>
                      <div className="flex-1">
                        <p className={cn(
                          'text-sm font-medium',
                          isDone && 'text-emerald-500',
                          isActive && 'text-primary',
                          isPending && 'text-muted-foreground',
                        )}>{label}</p>
                      </div>
                      {isActive && <div className="h-2 w-32 overflow-hidden rounded-full bg-muted"><div className="h-full w-full origin-left animate-progress rounded-full bg-primary" style={{ animationDuration: `${stageDurations[i]}ms` }} /></div>}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="space-y-4">
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

              {/* Classification results */}
              {result.classification && (
                <div>
                  <p className="mb-2 text-sm font-medium">Classification Results</p>
                  <div className="rounded-lg border">
                    {result.classification instanceof Array ? (
                      result.classification.map((c, i) => (
                        <div key={i} className="flex items-center justify-between border-b last:border-b-0 px-4 py-2.5">
                          <div>
                            <p className="text-sm font-medium">{c.category}</p>
                            <p className="text-xs text-muted-foreground">{c.sourceName} · detected by: {c.detectedBy}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={(c.confidence >= 0.8 ? 'success' : c.confidence >= 0.5 ? 'warning' : 'secondary') as 'success' | 'warning' | 'secondary'}>
                              {(c.confidence * 100).toFixed(0)}%
                            </Badge>
                            <Badge>{c.targetModules?.[0]}</Badge>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="flex items-center justify-between px-4 py-2.5">
                        <div>
                          <p className="text-sm font-medium">{(result.classification as ClassificationResult).category}</p>
                          <p className="text-xs text-muted-foreground">detected by: {(result.classification as ClassificationResult).detectedBy}</p>
                        </div>
                        <Badge>{(result.classification as ClassificationResult).targetModules?.[0]}</Badge>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Summary stats */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-lg border p-3 text-center">
                  <p className="text-2xl font-bold">{result.totalImported ?? 0}</p>
                  <p className="text-xs text-muted-foreground">Records Imported</p>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <p className="text-2xl font-bold">{result.evidenceGenerated ?? 0}</p>
                  <p className="text-xs text-muted-foreground">Evidence Created</p>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <p className="text-2xl font-bold">{result.recommendationsGenerated ? 'Yes' : 'No'}</p>
                  <p className="text-xs text-muted-foreground">Recommendations</p>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <p className="text-2xl font-bold">{result.reasoningTriggered ? 'Yes' : 'No'}</p>
                  <p className="text-xs text-muted-foreground">Reasoning Triggered</p>
                </div>
              </div>

              <div className="flex gap-3">
                <Button onClick={() => { setFile(null); setResult(null); setStage(0) }}>
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

      {/* Supported formats sidebar */}
      <Card>
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
        </CardContent>
      </Card>
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
