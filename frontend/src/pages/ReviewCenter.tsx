import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { Drawer } from '@/components/Drawer'
import { useReviewList, useReviewSummary, useApproveReview, useRejectReview, useRequestInfo, useAddComment, useAssignEngineer, useScheduleAction } from '@/services/reviewApiService'
import type { ReviewItem } from '@/types/review'
import {
  CheckCircle2, XCircle, MessageSquare, User, Calendar, AlertTriangle, ArrowRight, Activity
} from 'lucide-react'

const STATUS_BADGE: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
  under_review: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  more_info_needed: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  scheduled: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
}

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-yellow-500 text-slate-900',
  low: 'bg-slate-500 text-white',
}

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'more_info_needed', label: 'More Info Needed' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'scheduled', label: 'Scheduled' },
]

const PRIORITY_OPTIONS = [
  { value: '', label: 'All Priorities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const SUMMARY_CARDS = [
  { key: 'pending', label: 'Pending', color: 'border-l-slate-500' },
  { key: 'underReview', label: 'Under Review', color: 'border-l-blue-500' },
  { key: 'moreInfoNeeded', label: 'More Info', color: 'border-l-yellow-500' },
  { key: 'approved', label: 'Approved', color: 'border-l-green-500' },
  { key: 'rejected', label: 'Rejected', color: 'border-l-red-500' },
  { key: 'scheduled', label: 'Scheduled', color: 'border-l-purple-500' },
]

export default function ReviewCenter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedReview, setSelectedReview] = useState<ReviewItem | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'review' | 'comments' | 'audit'>('review')

  const search = searchParams.get('search') || ''
  const statusFilter = searchParams.get('status') || ''
  const priority = searchParams.get('priority') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const { data: listData, isLoading: listLoading, error: listError } = useReviewList({
    status: statusFilter || undefined,
    priority: priority || undefined,
    search: search || undefined,
    page,
    limit: 12,
  })
  const { data: summary } = useReviewSummary()

  const approveMutation = useApproveReview()
  const rejectMutation = useRejectReview()
  const requestInfoMutation = useRequestInfo()
  const addCommentMutation = useAddComment()
  const assignMutation = useAssignEngineer()
  const scheduleMutation = useScheduleAction()

  const items = (listData?.items ?? []).sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
  const total = listData?.total ?? 0
  const loading = listLoading
  const error = listError ? (listError as Error).message : null

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => {
      if (v) next.set(k, v)
      else next.delete(k)
    })
    if (updates.status !== undefined || updates.priority !== undefined || updates.search !== undefined) {
      next.delete('page')
    }
    setSearchParams(next)
  }

  const handleCardClick = (r: ReviewItem) => {
    setSelectedReview(r)
    setIsDrawerOpen(true)
    setActiveTab('review')
  }

  const [commentText, setCommentText] = useState('')
  const [rejectReason, setRejectReason] = useState('')
  const [infoQuestion, setInfoQuestion] = useState('')
  const [engineerEmail, setEngineerEmail] = useState('')
  const [scheduleDate, setScheduleDate] = useState('')
  const [showRejectInput, setShowRejectInput] = useState(false)
  const [showInfoInput, setShowInfoInput] = useState(false)
  const [showAssignInput, setShowAssignInput] = useState(false)
  const [showScheduleInput, setShowScheduleInput] = useState(false)

  const handleApprove = async () => {
    if (!selectedReview) return
    await approveMutation.mutateAsync({ reviewId: selectedReview.review_id, comment: '' })
    setSelectedReview({ ...selectedReview, status: 'approved' })
  }

  const handleReject = async () => {
    if (!selectedReview) return
    await rejectMutation.mutateAsync({ reviewId: selectedReview.review_id, reason: rejectReason })
    setSelectedReview({ ...selectedReview, status: 'rejected' })
    setShowRejectInput(false)
    setRejectReason('')
  }

  const handleRequestInfo = async () => {
    if (!selectedReview) return
    await requestInfoMutation.mutateAsync({ reviewId: selectedReview.review_id, question: infoQuestion })
    setSelectedReview({ ...selectedReview, status: 'more_info_needed' as any })
    setShowInfoInput(false)
    setInfoQuestion('')
  }

  const handleAddComment = async () => {
    if (!selectedReview || !commentText.trim()) return
    await addCommentMutation.mutateAsync({ reviewId: selectedReview.review_id, text: commentText })
    setCommentText('')
  }

  const handleAssign = async () => {
    if (!selectedReview || !engineerEmail.trim()) return
    await assignMutation.mutateAsync({ reviewId: selectedReview.review_id, engineer: engineerEmail })
    setSelectedReview({ ...selectedReview, assigned_engineer: engineerEmail })
    setShowAssignInput(false)
    setEngineerEmail('')
  }

  const handleSchedule = async () => {
    if (!selectedReview || !scheduleDate) return
    await scheduleMutation.mutateAsync({ reviewId: selectedReview.review_id, scheduledDate: scheduleDate })
    setSelectedReview({ ...selectedReview, status: 'scheduled' })
    setShowScheduleInput(false)
    setScheduleDate('')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Decision Review</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Review, approve, or reject AI-generated decisions before execution.
          </p>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {SUMMARY_CARDS.map((cfg) => {
            const count = (summary as any)[cfg.key] ?? 0
            return (
              <div key={cfg.key} className={`bg-card rounded-xl border shadow-xs border-l-4 ${cfg.color} px-4 py-3 transition-all`}>
                <div className="text-2xl font-bold text-foreground">{count}</div>
                <div className="text-xs font-medium text-muted-foreground mt-0.5">{cfg.label}</div>
              </div>
            )
          })}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3 bg-card p-4 rounded-xl border">
        <div className="flex-1 min-w-[280px]">
          <input
            type="text"
            placeholder="Search reviews by title or ID..."
            value={search}
            onChange={(e) => updateParams({ search: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <select value={statusFilter} onChange={(e) => updateParams({ status: e.target.value })} className="px-3 py-2 border rounded-lg bg-background text-sm">
            {STATUS_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <select value={priority} onChange={(e) => updateParams({ priority: e.target.value })} className="px-3 py-2 border rounded-lg bg-background text-sm">
            {PRIORITY_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      </div>

      {error && <ErrorState message={error} onRetry={() => window.location.reload()} />}
      {loading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" label="Loading reviews..." />
        </div>
      )}

      {!loading && !error && (
        <>
          {items.length === 0 ? (
            <EmptyState title="No reviews found" description="Adjust your search or filters." />
          ) : (
            <div className="space-y-3">
              {items.map((r) => (
                <div
                  key={r.review_id}
                  onClick={() => handleCardClick(r)}
                  className="bg-card rounded-xl border shadow-xs hover:shadow-md transition-all cursor-pointer p-5 flex flex-col md:flex-row md:items-center gap-4"
                >
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono text-muted-foreground">{r.review_id}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${PRIORITY_COLORS[r.priority] || ''}`}>{r.priority}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium capitalize ${STATUS_BADGE[r.status] || ''}`}>{r.status.replace(/_/g, ' ')}</span>
                    </div>
                    <h3 className="font-semibold text-sm leading-snug">{r.recommendation_title}</h3>
                    <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><User className="h-3 w-3" />{r.assigned_engineer || 'Unassigned'}</span>
                      <span className="flex items-center gap-1"><MessageSquare className="h-3 w-3" />{r.comments.length} comments</span>
                      <span className="flex items-center gap-1"><Activity className="h-3 w-3" />{r.audit_history.length} events</span>
                      <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                </div>
              ))}
            </div>
          )}

          {total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-6">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted transition-colors">Previous</button>
              <span className="text-sm text-muted-foreground">Page {page} of {Math.ceil(total / 12)}</span>
              <button disabled={page >= Math.ceil(total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted transition-colors">Next</button>
            </div>
          )}
        </>
      )}

      <Drawer open={isDrawerOpen} onOpenChange={(o) => { setIsDrawerOpen(o); if (!o) setSelectedReview(null) }} title={selectedReview?.recommendation_title || ''} description={selectedReview ? `Review ${selectedReview.review_id}` : ''}>
        {selectedReview && (
          <div className="space-y-6 pb-8">
            {/* Review Action Buttons */}
            <div className="flex flex-wrap gap-2 pb-2 border-b">
              <button
                onClick={handleApprove}
                disabled={selectedReview.status === 'approved' || approveMutation.isPending}
                className="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              ><CheckCircle2 className="h-4 w-4" /> Approve</button>
              <button
                onClick={() => setShowRejectInput(!showRejectInput)}
                disabled={selectedReview.status === 'rejected'}
                className="flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
              ><XCircle className="h-4 w-4" /> Reject</button>
              <button
                onClick={() => setShowInfoInput(!showInfoInput)}
                className="flex items-center gap-1.5 px-4 py-2 bg-yellow-600 text-white text-sm font-medium rounded-lg hover:bg-yellow-700 transition-colors"
              ><AlertTriangle className="h-4 w-4" /> Request Info</button>
              <button
                onClick={() => setShowAssignInput(!showAssignInput)}
                className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              ><User className="h-4 w-4" /> Assign</button>
              <button
                onClick={() => setShowScheduleInput(!showScheduleInput)}
                className="flex items-center gap-1.5 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
              ><Calendar className="h-4 w-4" /> Schedule</button>
            </div>

            {/* Inline inputs */}
            {showRejectInput && (
              <div className="space-y-2 p-3 bg-red-500/5 border border-red-500/20 rounded-lg">
                <textarea value={rejectReason} onChange={(e) => setRejectReason(e.target.value)} placeholder="Reason for rejection..." className="w-full px-3 py-2 border rounded-lg bg-background text-sm" rows={2} />
                <div className="flex gap-2">
                  <button onClick={handleReject} className="px-3 py-1.5 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700">Confirm Reject</button>
                  <button onClick={() => setShowRejectInput(false)} className="px-3 py-1.5 border text-sm rounded-lg hover:bg-muted">Cancel</button>
                </div>
              </div>
            )}
            {showInfoInput && (
              <div className="space-y-2 p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg">
                <textarea value={infoQuestion} onChange={(e) => setInfoQuestion(e.target.value)} placeholder="What additional information is needed?" className="w-full px-3 py-2 border rounded-lg bg-background text-sm" rows={2} />
                <div className="flex gap-2">
                  <button onClick={handleRequestInfo} className="px-3 py-1.5 bg-yellow-600 text-white text-sm rounded-lg hover:bg-yellow-700">Send Request</button>
                  <button onClick={() => setShowInfoInput(false)} className="px-3 py-1.5 border text-sm rounded-lg hover:bg-muted">Cancel</button>
                </div>
              </div>
            )}
            {showAssignInput && (
              <div className="space-y-2 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                <input value={engineerEmail} onChange={(e) => setEngineerEmail(e.target.value)} placeholder="Engineer email (e.g., name@xlventure.com)" className="w-full px-3 py-2 border rounded-lg bg-background text-sm" />
                <div className="flex gap-2">
                  <button onClick={handleAssign} className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Assign</button>
                  <button onClick={() => setShowAssignInput(false)} className="px-3 py-1.5 border text-sm rounded-lg hover:bg-muted">Cancel</button>
                </div>
              </div>
            )}
            {showScheduleInput && (
              <div className="space-y-2 p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
                <input type="date" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} className="w-full px-3 py-2 border rounded-lg bg-background text-sm" />
                <div className="flex gap-2">
                  <button onClick={handleSchedule} className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700">Schedule</button>
                  <button onClick={() => setShowScheduleInput(false)} className="px-3 py-1.5 border text-sm rounded-lg hover:bg-muted">Cancel</button>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex border-b gap-4 text-sm">
              {(['review', 'comments', 'audit'] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`pb-2 font-medium capitalize border-b-2 transition-colors ${activeTab === tab ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}>
                  {tab === 'review' ? 'Review Details' : tab === 'comments' ? `Comments (${selectedReview.comments.length})` : `Audit History (${selectedReview.audit_history.length})`}
                </button>
              ))}
            </div>

            {activeTab === 'review' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Status</span><span className={`inline-block text-xs px-2 py-0.5 rounded font-medium mt-1 capitalize ${STATUS_BADGE[selectedReview.status] || ''}`}>{selectedReview.status.replace(/_/g, ' ')}</span></div>
                  <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Priority</span><span className={`inline-block text-xs px-2 py-0.5 rounded font-bold uppercase mt-1 ${PRIORITY_COLORS[selectedReview.priority] || ''}`}>{selectedReview.priority}</span></div>
                  <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Assigned Engineer</span><span className="font-medium text-sm text-foreground block mt-1">{selectedReview.assigned_engineer || <span className="text-muted-foreground italic">Not assigned</span>}</span></div>
                  <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Recommendation</span><span className="font-medium text-sm text-foreground block mt-1">{selectedReview.recommendation_id}</span></div>
                </div>
              </div>
            )}

            {activeTab === 'comments' && (
              <div className="space-y-4">
                {selectedReview.comments.length === 0 ? (
                  <p className="text-sm text-muted-foreground italic">No comments yet.</p>
                ) : (
                  selectedReview.comments.map((c) => (
                    <div key={c.id} className="bg-card p-3 rounded-lg border text-sm space-y-1">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="font-medium text-foreground">{c.author}</span>
                        <span>{new Date(c.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-foreground">{c.text}</p>
                    </div>
                  ))
                )}
                <div className="flex gap-2">
                  <input value={commentText} onChange={(e) => setCommentText(e.target.value)} placeholder="Add a comment..." className="flex-1 px-3 py-2 border rounded-lg bg-background text-sm" onKeyDown={(e) => { if (e.key === 'Enter') handleAddComment() }} />
                  <button onClick={handleAddComment} disabled={!commentText.trim()} className="px-4 py-2 bg-primary text-primary-foreground text-sm rounded-lg hover:bg-primary/90 disabled:opacity-50">Send</button>
                </div>
              </div>
            )}

            {activeTab === 'audit' && (
              <div className="space-y-2">
                {selectedReview.audit_history.map((entry, idx) => (
                  <div key={idx} className="flex gap-3 text-sm">
                    <div className="flex flex-col items-center">
                      <div className="h-2.5 w-2.5 rounded-full bg-primary/60" />
                      {idx < selectedReview.audit_history.length - 1 && <div className="w-px flex-1 bg-border" />}
                    </div>
                    <div className="pb-4 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize text-foreground">{entry.action.replace(/_/g, ' ')}</span>
                        <span className="text-xs text-muted-foreground">by {entry.by}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{entry.detail}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{new Date(entry.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  )
}
