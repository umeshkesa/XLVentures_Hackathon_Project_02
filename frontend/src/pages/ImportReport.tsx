import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorState } from '@/components/ErrorState'
import { EmptyState } from '@/components/EmptyState'
import { useImportService } from '@/services/importService'
import type { ImportReport as ReportData, ClassificationResult } from '@/types/import'

export default function ImportReport() {
  const { jobId } = useParams<{ jobId: string }>()
  const svc = useImportService()
  const [report, setReport] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    if (!jobId) return
    setLoading(true)
    svc.getReport(jobId).then((r) => {
      setReport(r)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load report')
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [jobId]) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="flex justify-center py-16"><LoadingSpinner label="Loading report..." /></div>
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!report) return <ErrorState title="Report not found" message={`No report for job ${jobId}`} />

  const classification = report.classification
  const summary = report.importSummary ?? {}
  const recommendations = report.recommendations ?? {}
  const isCompleted = report.status === 'completed'
  const isFailed = report.status === 'failed'

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/import"><ArrowLeft className="h-5 w-5" /></Link>
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">Import Report</h1>
            <Badge variant={isCompleted ? 'success' : isFailed ? 'destructive' : 'warning'}>
              {report.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">{report.filename} · {new Date(report.createdAt).toLocaleString()}</p>
        </div>
      </div>

      {/* Status banner */}
      {isCompleted ? (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
          <CheckCircle2 className="h-6 w-6 text-emerald-500" />
          <div>
            <p className="font-medium text-emerald-600 dark:text-emerald-400">Import completed successfully</p>
            <p className="text-sm text-muted-foreground">Job ID: {report.jobId}</p>
          </div>
        </div>
      ) : isFailed ? (
        <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 p-4">
          <XCircle className="h-6 w-6 text-red-500" />
          <div>
            <p className="font-medium text-red-600 dark:text-red-400">Import failed</p>
            {report.error && <p className="text-sm text-muted-foreground">{report.error}</p>}
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
          <AlertCircle className="h-6 w-6 text-amber-500" />
          <div>
            <p className="font-medium text-amber-600 dark:text-amber-400">Import in progress</p>
            <p className="text-sm text-muted-foreground">{report.progress}% complete</p>
          </div>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Classification */}
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Classification</CardTitle></CardHeader>
          <CardContent>
            {!classification ? (
              <EmptyState title="No classification data" />
            ) : classification instanceof Array ? (
              <div className="space-y-2">
                {classification.map((c: ClassificationResult, i: number) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{c.category}</p>
                      <p className="text-xs text-muted-foreground">{c.sourceName} · {c.detectedBy}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={(c.confidence >= 0.8 ? 'success' : c.confidence >= 0.5 ? 'warning' : 'secondary') as 'success' | 'warning' | 'secondary'}>
                        {(c.confidence * 100).toFixed(0)}%
                      </Badge>
                      <Badge>{c.targetModules?.[0] ?? '—'}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">{(classification as ClassificationResult).category}</p>
                  <p className="text-xs text-muted-foreground">detected by: {(classification as ClassificationResult).detectedBy}</p>
                </div>
                <Badge>{(classification as ClassificationResult).targetModules?.[0]}</Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Import Summary */}
        <Card>
          <CardHeader><CardTitle>Import Summary</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {Object.keys(summary).length === 0 ? (
              <EmptyState title="No summary data" />
            ) : (
              Object.entries(summary).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="font-medium">{String(value)}</span>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card>
          <CardHeader><CardTitle>Recommendations</CardTitle></CardHeader>
          <CardContent>
            {Object.keys(recommendations).length === 0 ? (
              <EmptyState title="No recommendations generated" />
            ) : (
              <div className="space-y-2">
                {Object.entries(recommendations).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{String(value)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* File info */}
      <Card>
        <CardHeader><CardTitle>File Information</CardTitle></CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Filename</p>
            <p className="font-medium">{report.filename}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">File Type</p>
            <p className="font-medium uppercase">{report.fileType.replace('.', '')}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Created</p>
            <p className="font-medium">{new Date(report.createdAt).toLocaleString()}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Completed</p>
            <p className="font-medium">{report.completedAt ? new Date(report.completedAt).toLocaleString() : '—'}</p>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button variant="outline" asChild>
          <Link to="/import"><ArrowLeft className="h-4 w-4" /> Back to Import Center</Link>
        </Button>
        <Button onClick={load} variant="secondary">Refresh Report</Button>
      </div>
    </div>
  )
}
