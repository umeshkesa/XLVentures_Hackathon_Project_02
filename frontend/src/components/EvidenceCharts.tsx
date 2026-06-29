import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Cell,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import { EmptyState } from './EmptyState'
import type { EvidenceAnalytics } from '@/types/dashboard'

interface Props {
  data: EvidenceAnalytics
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

function BarWidget({ title, data }: { title: string; data: { name: string; value: number; color: string }[] }) {
  const sorted = [...data].sort((a, b) => b.value - a.value)
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={sorted} margin={{ top: 4, right: 4, bottom: 4, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }}
            axisLine={{ stroke: 'var(--border)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--popover)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              fontSize: 13,
            }}
            formatter={(value) => [typeof value === 'number' ? value.toLocaleString() : String(value), 'Count']}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={48}>
            {sorted.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function EvidenceCharts({ data, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Evidence Analytics</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evidence Analytics</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading charts..." /></div>
        ) : data.byType.length === 0 ? (
          <EmptyState title="No evidence data" />
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            <BarWidget title="Evidence by Type" data={data.byType} />
            <BarWidget title="Evidence by Source" data={data.bySource} />
            <BarWidget title="Evidence Confidence" data={data.confidence} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
