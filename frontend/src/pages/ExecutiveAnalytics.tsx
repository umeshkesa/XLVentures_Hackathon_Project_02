import { useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area, Legend,
} from 'recharts'
import { useRecommendationList } from '@/services/recommendationApiService'
import { useEvidence } from '@/services/evidenceApiService'
import { useKnowledge } from '@/services/knowledgeApiService'
import { useReasoningList } from '@/services/reasoningApiService'
import { useImportJobs } from '@/services/healthApiService'
import { ANALYTICS_COLORS } from '@/types/analytics'
import { Card } from '@/components/Card'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import {
  TrendingUp, FileSearch, BookOpen, Upload, BrainCircuit, ThumbsUp,
} from 'lucide-react'

export default function ExecutiveAnalytics() {
  const { data: recs, isLoading: recsLoading } = useRecommendationList({ limit: 100 })
  const { data: evData, isLoading: evLoading } = useEvidence({ limit: 100 })
  const { data: knowledgeData, isLoading: knLoading } = useKnowledge({ limit: 100 })
  const { data: reasonData, isLoading: rsLoading } = useReasoningList({ limit: 100 })
  const { data: importJobs = [] } = useImportJobs()

  const recommendations = recs?.items ?? []
  const evidence = evData?.items ?? []
  const knowledge = knowledgeData?.items ?? []
  const reasoning = reasonData?.items ?? []

  const loading = recsLoading || evLoading || knLoading || rsLoading

  const statusData = useMemo(() => {
    const counts: Record<string, number> = {}
    recommendations.forEach(r => { const s = r.status || 'unknown'; counts[s] = (counts[s] || 0) + 1 })
    return Object.entries(counts).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }))
  }, [recommendations])

  const priorityData = useMemo(() => {
    const counts: Record<string, number> = {}
    recommendations.forEach(r => { const p = r.priority || 'unknown'; counts[p] = (counts[p] || 0) + 1 })
    return Object.entries(counts).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }))
  }, [recommendations])

  const confidenceData = useMemo(() => {
    const buckets = [0, 0, 0, 0, 0]
    recommendations.forEach(r => {
      const c = r.confidence ?? 0
      if (c >= 0.9) buckets[4]++
      else if (c >= 0.7) buckets[3]++
      else if (c >= 0.5) buckets[2]++
      else if (c >= 0.3) buckets[1]++
      else buckets[0]++
    })
    return [
      { name: '0-30%', value: buckets[0] },
      { name: '30-50%', value: buckets[1] },
      { name: '50-70%', value: buckets[2] },
      { name: '70-90%', value: buckets[3] },
      { name: '90-100%', value: buckets[4] },
    ]
  }, [recommendations])

  const evidenceGrowth = useMemo(() => {
    const monthly: Record<string, number> = {}
    evidence.forEach(e => {
      if (e.timestamp) {
        const m = e.timestamp.substring(0, 7)
        monthly[m] = (monthly[m] || 0) + 1
      }
    })
    return Object.entries(monthly).sort().map(([date, count]) => ({ date, count }))
  }, [evidence])

  const activityTimeline = useMemo(() => {
    const monthly: Record<string, { recommendations: number; evidence: number; reasoning: number }> = {}
    const add = (date: string | undefined, key: 'recommendations' | 'evidence' | 'reasoning') => {
      if (date) {
        const m = date.substring(0, 7)
        if (!monthly[m]) monthly[m] = { recommendations: 0, evidence: 0, reasoning: 0 }
        monthly[m][key]++
      }
    }
    recommendations.forEach(r => add(r.createdAt, 'recommendations'))
    evidence.forEach(e => add(e.timestamp, 'evidence'))
    reasoning.forEach(r => add(r.createdAt, 'reasoning'))
    return Object.entries(monthly).sort().map(([date, vals]) => ({ date, ...vals }))
  }, [recommendations, evidence, reasoning])

  const summaryCards = useMemo(() => [
    { label: 'Recommendations', value: recommendations.length, icon: <ThumbsUp className="h-4 w-4" />, color: 'text-orange-500' },
    { label: 'Evidence Items', value: evidence.length, icon: <FileSearch className="h-4 w-4" />, color: 'text-amber-500' },
    { label: 'Knowledge Docs', value: knowledge.length, icon: <BookOpen className="h-4 w-4" />, color: 'text-emerald-500' },
    { label: 'Dataset Imports', value: importJobs.length, icon: <Upload className="h-4 w-4" />, color: 'text-blue-500' },
    { label: 'Reasoning Sessions', value: reasoning.length, icon: <BrainCircuit className="h-4 w-4" />, color: 'text-violet-500' },
    { label: 'Avg Confidence', value: recommendations.length ? `${Math.round(recommendations.reduce((s, r) => s + (r.confidence ?? 0), 0) / recommendations.length * 100)}%` : '—', icon: <TrendingUp className="h-4 w-4" />, color: 'text-cyan-500' },
  ], [recommendations, evidence, knowledge, importJobs, reasoning])

  if (loading) return <div className="flex justify-center py-12"><LoadingSpinner /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Executive Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">Platform-wide analytics and business impact metrics</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {summaryCards.map(card => (
          <Card key={card.label} className="p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-muted-foreground uppercase">{card.label}</span>
              <span className={card.color}>{card.icon}</span>
            </div>
            <div className="text-xl font-bold">{card.value}</div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-4">
          <h3 className="text-sm font-semibold mb-4">Recommendations by Status</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
                  {statusData.map((_, i) => (<Cell key={i} fill={ANALYTICS_COLORS[i % ANALYTICS_COLORS.length]} />))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-sm font-semibold mb-4">Recommendations by Priority</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {priorityData.map((_, i) => (<Cell key={i} fill={ANALYTICS_COLORS[i % ANALYTICS_COLORS.length]} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-sm font-semibold mb-4">Confidence Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {confidenceData.map((_, i) => (<Cell key={i} fill={ANALYTICS_COLORS[i % ANALYTICS_COLORS.length]} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-sm font-semibold mb-4">Evidence Growth</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evidenceGrowth.length > 0 ? evidenceGrowth : [{ date: 'No data', count: 0 }]}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke={ANALYTICS_COLORS[0]} fill={ANALYTICS_COLORS[0]} fillOpacity={0.2} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card className="p-4">
        <h3 className="text-sm font-semibold mb-4">System Activity Timeline</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={activityTimeline.length > 0 ? activityTimeline : [{ date: 'No data', recommendations: 0, evidence: 0, reasoning: 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Line type="monotone" dataKey="recommendations" stroke={ANALYTICS_COLORS[5]} strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="evidence" stroke={ANALYTICS_COLORS[1]} strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="reasoning" stroke={ANALYTICS_COLORS[4]} strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-500">
            {recommendations.length > 0
              ? `${Math.round(recommendations.filter(r => r.status === 'approved' || r.status === 'active').length / recommendations.length * 100)}%`
              : '—'}
          </div>
          <div className="text-xs text-muted-foreground mt-1">Decision Approval Rate</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-amber-500">
            {recommendations.length > 0
              ? recommendations.filter(r => r.riskLevel === 'high' || r.riskLevel === 'critical').length
              : '0'}
          </div>
          <div className="text-xs text-muted-foreground mt-1">High Risk Items</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-500">
            {reasoning.length}
          </div>
          <div className="text-xs text-muted-foreground mt-1">Agent Utilization (Sessions)</div>
        </Card>
      </div>
    </div>
  )
}
