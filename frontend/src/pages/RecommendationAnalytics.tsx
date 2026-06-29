import { useMemo } from 'react'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorState } from '@/components/ErrorState'
import { useRecommendationList } from '@/services/recommendationApiService'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const PRIORITY_COLORS: Record<string, string> = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#64748b' }
const STATUS_COLORS: Record<string, string> = { active: '#3b82f6', pending_approval: '#eab308', approved: '#22c55e', rejected: '#ef4444', executed: '#06b6d4', draft: '#94a3b8' }
const RISK_COLORS: Record<string, string> = { high: '#ef4444', medium: '#f97316', low: '#22c55e' }
const EXECUTION_COLORS: Record<string, string> = { pending: '#94a3b8', in_progress: '#3b82f6', completed: '#22c55e', cancelled: '#ef4444' }
const APPROVAL_COLORS: Record<string, string> = { approved: '#22c55e', rejected: '#ef4444', pending: '#eab308' }

export default function RecommendationAnalytics() {
  const { data: listData, isLoading, error } = useRecommendationList({ limit: 100 })
  const items = listData?.items ?? []

  const priorityData = useMemo(() =>
    ['critical', 'high', 'medium', 'low'].map((p) => ({
      name: p.charAt(0).toUpperCase() + p.slice(1),
      value: items.filter((r) => r.priority === p).length,
      fill: PRIORITY_COLORS[p],
    })), [items])

  const statusData = useMemo(() =>
    ['active', 'pending_approval', 'approved', 'rejected', 'executed', 'draft'].map((s) => ({
      name: s.replace(/_/g, ' '),
      value: items.filter((r) => r.status === s).length,
      fill: STATUS_COLORS[s],
    })), [items])

  const riskData = useMemo(() =>
    ['high', 'medium', 'low'].map((r) => ({
      name: r.charAt(0).toUpperCase() + r.slice(1),
      value: items.filter((i) => i.riskLevel === r).length,
      fill: RISK_COLORS[r],
    })), [items])

  const approvalData = useMemo(() => {
    const approved = items.filter((r) => r.status === 'approved').length
    const rejected = items.filter((r) => r.status === 'rejected').length
    const pending = items.filter((r) => r.status === 'pending_approval' || r.status === 'active').length
    return [
      { name: 'Approved', value: approved, fill: APPROVAL_COLORS.approved },
      { name: 'Rejected', value: rejected, fill: APPROVAL_COLORS.rejected },
      { name: 'Pending', value: pending, fill: APPROVAL_COLORS.pending },
    ]
  }, [items])

  const executionData = useMemo(() =>
    ['pending', 'in_progress', 'completed', 'cancelled'].map((s) => ({
      name: s.replace(/_/g, ' '),
      value: items.filter((r) => {
        if (s === 'pending') return r.status === 'active' || r.status === 'pending_approval'
        if (s === 'in_progress') return r.status === 'approved'
        if (s === 'completed') return r.status === 'executed'
        if (s === 'cancelled') return r.status === 'rejected'
        return false
      }).length,
      fill: EXECUTION_COLORS[s],
    })), [items])

  const impactData = useMemo(() => {
    const categories = [...new Set(items.map((r) => r.businessImpact?.split('.')[0]?.trim() || '').filter(Boolean))]
    return categories.slice(0, 8).map((cat) => ({
      name: cat.length > 20 ? cat.slice(0, 20) + '...' : cat,
      value: items.filter((r) => r.businessImpact?.startsWith(cat)).length,
    }))
  }, [items])

  const sourceData = useMemo(() =>
    [...new Set(items.map((r) => r.source))].map((s) => ({
      name: s.replace(/_/g, ' '),
      value: items.filter((r) => r.source === s).length,
    })), [items])

  const confidenceData = useMemo(() => [
    { range: '0-50%', count: items.filter((r) => r.confidence <= 0.5).length },
    { range: '50-70%', count: items.filter((r) => r.confidence > 0.5 && r.confidence <= 0.7).length },
    { range: '70-85%', count: items.filter((r) => r.confidence > 0.7 && r.confidence <= 0.85).length },
    { range: '85-95%', count: items.filter((r) => r.confidence > 0.85 && r.confidence <= 0.95).length },
    { range: '95-100%', count: items.filter((r) => r.confidence > 0.95).length },
  ], [items])

  const costSavingsData = useMemo(() =>
    items.slice(0, 10).map((r) => ({
      name: r.id,
      cost: r.estimatedCost,
      savings: r.estimatedSavings,
    })), [items])

  if (error) return <ErrorState message={(error as Error).message} onRetry={() => window.location.reload()} />
  if (isLoading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Recommendation Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Visual analysis of recommendation distribution, confidence, financial impact, and execution pipeline
        </p>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-12 text-slate-500">No recommendation data available for analytics.</div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <div className="text-xs text-slate-500">Total Recommendations</div>
              <div className="text-2xl font-bold mt-1">{items.length}</div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <div className="text-xs text-slate-500">Avg Confidence</div>
              <div className="text-2xl font-bold mt-1">{(items.reduce((a, r) => a + r.confidence, 0) / items.length * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <div className="text-xs text-slate-500">Total Estimated Cost</div>
              <div className="text-2xl font-bold mt-1">${items.reduce((a, r) => a + (r.estimatedCost || 0), 0).toLocaleString()}</div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <div className="text-xs text-slate-500">Total Estimated Savings</div>
              <div className="text-2xl font-bold mt-1 text-green-600">${items.reduce((a, r) => a + (r.estimatedSavings || 0), 0).toLocaleString()}</div>
            </div>
          </div>

          {/* Distribution Pie Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">By Priority</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={priorityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }: any) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {priorityData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">Approval Rate</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={approvalData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }: any) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {approvalData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">Execution Status</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={executionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }: any) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {executionData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Additional Distribution Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">By Risk Level</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ percent }: any) => `${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {riskData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">By Status</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ percent }: any) => `${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {statusData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">Top Impact Categories</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={impactData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">Confidence Distribution</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={confidenceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="text-sm font-semibold mb-3">By Source</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sourceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 className="text-sm font-semibold mb-3">Cost vs Savings (Top 10)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={costSavingsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
                <Tooltip formatter={(value: any) => `$${(value ?? 0).toLocaleString()}`} />
                <Legend />
                <Bar dataKey="cost" fill="#ef4444" name="Cost" radius={[4, 4, 0, 0]} />
                <Bar dataKey="savings" fill="#22c55e" name="Savings" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}
