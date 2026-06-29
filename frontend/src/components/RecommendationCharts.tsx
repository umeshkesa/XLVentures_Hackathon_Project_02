import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, type PieLabelRenderProps,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import { EmptyState } from './EmptyState'
import type { RecommendationOverview } from '@/types/dashboard'

interface Props {
  data: RecommendationOverview
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

function renderLabel(props: PieLabelRenderProps) {
  const { cx, cy, midAngle, innerRadius, outerRadius, percent } = props
  if (midAngle == null || percent == null) return null
  const RADIAN = Math.PI / 180
  const radius = (innerRadius as number) + ((outerRadius as number) - (innerRadius as number)) * 0.5
  const x = (cx as number) + radius * Math.cos(-(midAngle as number) * RADIAN)
  const y = (cy as number) + radius * Math.sin(-(midAngle as number) * RADIAN)
  if (percent < 0.05) return null
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={600}>
      {(percent * 100).toFixed(0)}%
    </text>
  )
}

function PieWidget({ title, data }: { title: string; data: { name: string; value: number; color: string }[] }) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            dataKey="value"
            label={renderLabel}
            labelLine={false}
          >
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: 'var(--popover)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              fontSize: 13,
            }}
            formatter={(value) => [typeof value === 'number' ? value.toLocaleString() : String(value)]}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap justify-center gap-3">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-muted-foreground">{d.name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function RecommendationCharts({ data, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Recommendation Overview</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommendation Overview</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading charts..." /></div>
        ) : data.byPriority.length === 0 ? (
          <EmptyState title="No recommendation data" />
        ) : (
          <div className="grid gap-6 sm:grid-cols-3">
            <PieWidget title="By Priority" data={data.byPriority} />
            <PieWidget title="By Status" data={data.byStatus} />
            <PieWidget title="Confidence Distribution" data={data.confidenceDistribution} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
