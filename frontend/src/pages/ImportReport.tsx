import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Tag,
  Database,
  BookOpen,
  Scale,
  BrainCircuit,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorState } from '@/components/ErrorState'
import { EmptyState } from '@/components/EmptyState'
import { cn } from '@/lib/utils'
import { useImportService } from '@/services/importService'
import type { ImportReport as ReportData, ClassificationResult, RecommendationDetail } from '@/types/import'

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
  const recommendations = report.recommendations ?? ({} as Record<string, unknown>)
  const pipelineStages = report.pipelineStages ?? []
  const isCompleted = report.status === 'completed'
  const isFailed = report.status === 'failed'

  const recDetails = (recommendations as Record<string, unknown>).recommendationDetails as RecommendationDetail | undefined

  const classificationReason = (summary as Record<string, unknown>).classificationReason as string ?? ''
  const sRecommendation = (summary as Record<string, unknown>).recommendation as string ?? ''
  const sConfidence = (summary as Record<string, unknown>).confidence as number ?? 0
  const sReasoning = (summary as Record<string, unknown>).reasoning as string ?? ''
  const sEvidenceIds = (summary as Record<string, unknown>).evidenceIds as string[] ?? []
  const sKnowledgeIds = (summary as Record<string, unknown>).knowledgeIds as string[] ?? []
  const sRuleIds = (summary as Record<string, unknown>).ruleIds as string[] ?? []
  const sIssue = (summary as Record<string, unknown>).issue as string ?? ''
  const sSeverity = (summary as Record<string, unknown>).severity as string ?? ''

  const issue = sIssue || recDetails?.issue || 'Data Analysis'
  const severity = sSeverity || recDetails?.severity || 'medium'
  const recommendation = sRecommendation || recDetails?.recommendation || recDetails?.conclusion || recDetails?.primaryRecommendation || ''
  const confidence = sConfidence || recDetails?.confidenceScore || recDetails?.confidence || 0
  const reasoning = sReasoning || recDetails?.reasoning || recDetails?.reasoningSummary || ''
  const evidence = sEvidenceIds?.length > 0 ? sEvidenceIds : (recDetails?.evidence ?? [])
  const knowledge = sKnowledgeIds?.length > 0 ? sKnowledgeIds : (recDetails?.knowledge ?? [])
  const rules = sRuleIds?.length > 0 ? sRuleIds : (recDetails?.rules ?? [])

  return (
    <div className="space-y-6 max-w-5xl">
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

      <div className="grid gap-6 md:grid-cols-3">
        {/* Classification */}
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Classification</CardTitle></CardHeader>
          <CardContent>
            {!classification ? (
              <EmptyState title="No classification data" />
            ) : classification instanceof Array ? (
              <div className="space-y-3">
                {classification.map((c: ClassificationResult, i: number) => (
                  <div key={i} className="rounded-lg border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Tag className="h-4 w-4 text-blue-500" />
                        <div>
                          <p className="font-semibold text-foreground">{c.category}</p>
                          <p className="text-xs text-muted-foreground">{c.sourceName} · {c.detectedBy}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={(c.confidence >= 0.8 ? 'success' : c.confidence >= 0.5 ? 'warning' : 'secondary') as 'success' | 'warning' | 'secondary'}>
                          {(c.confidence * 100).toFixed(0)}%
                        </Badge>
                        <Badge>{c.targetModules?.[0] ?? '—'}</Badge>
                      </div>
                    </div>
                    {(c as any).classificationReason && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground border-t pt-2">
                        <span className="font-medium text-foreground">Reason:</span>
                        <span className="italic">{(c as any).classificationReason}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Tag className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="font-semibold text-foreground">{(classification as ClassificationResult).category}</p>
                      <p className="text-xs text-muted-foreground">detected by: {(classification as ClassificationResult).detectedBy}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge>{(classification as ClassificationResult).targetModules?.[0]}</Badge>
                    <Badge variant={(classification as ClassificationResult).confidence >= 0.8 ? 'success' : (classification as ClassificationResult).confidence >= 0.5 ? 'warning' : 'secondary'}>
                      {((classification as ClassificationResult).confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
                {(classification as any).classificationReason && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground border-t pt-2">
                    <span className="font-medium text-foreground">Reason:</span>
                    <span className="italic">{(classification as any).classificationReason}</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pipeline Stages */}
        <Card>
          <CardHeader><CardTitle>Pipeline Stages</CardTitle></CardHeader>
          <CardContent>
            {pipelineStages.length === 0 ? (
              <EmptyState title="No pipeline data" />
            ) : (
              <div className="space-y-2">
                {pipelineStages.map((stage) => (
                  <div key={stage.name} className="flex items-center gap-2 text-xs">
                    {stage.status === 'completed' && <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />}
                    {stage.status === 'in_progress' && <div className="h-3 w-3 rounded-full border-2 border-blue-500 border-t-transparent animate-spin shrink-0" />}
                    {stage.status === 'failed' && <XCircle className="h-3 w-3 text-red-500 shrink-0" />}
                    {stage.status === 'pending' && <Clock className="h-3 w-3 text-slate-400 shrink-0" />}
                    <span className={cn(
                      'flex-1',
                      stage.status === 'completed' && 'text-emerald-700 dark:text-emerald-300',
                      stage.status === 'failed' && 'text-red-600 dark:text-red-400',
                      stage.status === 'in_progress' && 'text-blue-600 dark:text-blue-400 font-medium',
                      stage.status === 'pending' && 'text-slate-400',
                    )}>{stage.label}</span>
                    {stage.durationMs > 0 && (
                      <span className="text-slate-400 font-mono">{stage.durationMs}ms</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recommendation Details - Enterprise Cards */}
      {recommendation && (
        <Card>
          <CardHeader><CardTitle>Recommendation Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Issue</p>
                  <p className="font-semibold text-foreground mt-1">{issue}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Severity</p>
                  <Badge
                    variant={severity === 'critical' ? 'destructive' : severity === 'high' ? 'warning' : 'secondary'}
                    className="mt-1"
                  >
                    {severity}
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Recommendation</p>
                  <p className="font-medium text-foreground mt-1">{recommendation}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Confidence</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                      <div
                        className={cn(
                          'h-full rounded-full',
                          confidence >= 0.7 ? 'bg-emerald-500' : confidence >= 0.4 ? 'bg-amber-500' : 'bg-red-500',
                        )}
                        style={{ width: `${confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold">{(confidence * 100).toFixed(0)}%</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {reasoning && (
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Reasoning</p>
                  <p className="text-sm text-foreground mt-1 flex items-start gap-2">
                    <BrainCircuit className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" />
                    <span>{reasoning}</span>
                  </p>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-4 sm:grid-cols-3">
              {evidence.length > 0 && (
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                      <Database className="h-3 w-3 text-purple-500" /> Evidence Used
                    </p>
                    <div className="space-y-1 mt-2">
                      {evidence.map((id: string) => (
                        <div key={id} className="flex items-center gap-1.5 text-xs">
                          <Database className="h-3 w-3 text-purple-500 shrink-0" />
                          <Link to={`/evidence/${id}`} className="text-blue-600 dark:text-blue-400 hover:underline">{id}</Link>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {knowledge.length > 0 && (
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                      <BookOpen className="h-3 w-3 text-yellow-500" /> Knowledge Retrieved
                    </p>
                    <div className="space-y-1 mt-2">
                      {knowledge.map((id: string) => (
                        <div key={id} className="flex items-center gap-1.5 text-xs">
                          <BookOpen className="h-3 w-3 text-yellow-500 shrink-0" />
                          <Link to={`/knowledge/${id}`} className="text-blue-600 dark:text-blue-400 hover:underline">{id}</Link>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {rules.length > 0 && (
                <Card>
                  <CardContent className="pt-4">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                      <Scale className="h-3 w-3 text-orange-500" /> Rules Triggered
                    </p>
                    <div className="space-y-1 mt-2">
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

            {/* Explainability: Alternative Actions */}
            {recDetails?.explainability && recDetails.explainability.alternativeActions.length > 0 && (
              <Card>
                <CardContent className="pt-4">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Alternative Actions Considered</p>
                  <div className="space-y-2">
                    {recDetails.explainability.alternativeActions.map((alt, i) => (
                      <div key={i} className="flex items-center justify-between text-xs p-2.5 bg-muted/50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3 text-slate-400" />
                          <span className="font-medium text-foreground">{alt.title}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            <div className="h-1.5 w-12 overflow-hidden rounded-full bg-muted">
                              <div className={cn(
                                'h-full rounded-full',
                                alt.confidence >= 0.7 ? 'bg-emerald-500' : alt.confidence >= 0.4 ? 'bg-amber-500' : 'bg-red-500',
                              )} style={{ width: `${alt.confidence * 100}%` }} />
                            </div>
                            <span className="text-muted-foreground">{(alt.confidence * 100).toFixed(0)}%</span>
                          </div>
                          <span className="text-muted-foreground italic max-w-[200px] truncate">{alt.reason}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      )}

      {/* Import Summary */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Import Summary</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">{((summary as Record<string, unknown>)?.importedCount as number) ?? ((summary as Record<string, unknown>)?.rowsImported as number) ?? ((summary as Record<string, unknown>)?.totalImported as number) ?? 0}</p>
                <p className="text-xs text-muted-foreground">Records Imported</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">{(summary as Record<string, unknown>)?.evidenceGenerated as number ?? 0}</p>
                <p className="text-xs text-muted-foreground">Evidence Created</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">{(recommendations as Record<string, unknown>)?.nextBestAction ? 'Yes' : '—'}</p>
                <p className="text-xs text-muted-foreground">Recommendations</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">{(recommendations as Record<string, unknown>)?.reasoning ? 'Yes' : '—'}</p>
                <p className="text-xs text-muted-foreground">Reasoning Triggered</p>
              </div>
            </div>
            {classificationReason && (
              <div className="rounded-lg bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-3 text-sm">
                <span className="font-medium text-blue-700 dark:text-blue-300">Classification Reason: </span>
                <span className="text-blue-600 dark:text-blue-400 italic">{classificationReason}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* File Info */}
        <Card>
          <CardHeader><CardTitle>File Information</CardTitle></CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
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
      </div>

      {/* Pipeline Stages Visual Timeline */}
      {pipelineStages.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Pipeline Execution Timeline</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {pipelineStages.map((stage, idx) => (
                <div key={stage.name} className="flex items-center gap-3 py-2">
                  <div className={cn(
                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold',
                    stage.status === 'completed' && 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
                    stage.status === 'failed' && 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
                    stage.status === 'in_progress' && 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
                    stage.status === 'pending' && 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500',
                  )}>
                    {stage.status === 'completed' ? <CheckCircle2 className="h-3.5 w-3.5" /> : idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={cn(
                      'text-sm font-medium',
                      stage.status === 'completed' && 'text-emerald-700 dark:text-emerald-300',
                      stage.status === 'failed' && 'text-red-600 dark:text-red-400',
                      stage.status === 'in_progress' && 'text-blue-600 dark:text-blue-400',
                      stage.status === 'pending' && 'text-slate-400',
                    )}>{stage.label}</p>
                  </div>
                  {stage.durationMs > 0 && (
                    <span className="text-xs text-slate-400 font-mono">{stage.durationMs}ms</span>
                  )}
                  {stage.startedAt && (
                    <span className="text-xs text-slate-400 font-mono">{new Date(stage.startedAt).toLocaleTimeString()}</span>
                  )}
                  <Badge variant={stage.status === 'completed' ? 'success' : stage.status === 'failed' ? 'destructive' : 'secondary'} className="text-[10px]">
                    {stage.status === 'in_progress' ? 'Running' : stage.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex gap-3">
        <Button variant="outline" asChild>
          <Link to="/import"><ArrowLeft className="h-4 w-4" /> Back to Import Center</Link>
        </Button>
        <Button onClick={load} variant="secondary">Refresh Report</Button>
      </div>
    </div>
  )
}
