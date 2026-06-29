import { cn } from '@/lib/utils'
import {
  Sun,
  Wind,
  Zap,
  BatteryCharging,
  Radio,
  TrendingUp,
  TrendingDown,
  type LucideIcon,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import { EmptyState } from './EmptyState'
import type { AssetOverview as AssetData } from '@/types/dashboard'

const assetIcons: Record<string, LucideIcon> = {
  Sun,
  Wind,
  Zap,
  BatteryCharging,
  Radio,
}

const statusDot: Record<string, string> = {
  online: 'bg-emerald-500',
  offline: 'bg-red-500',
  warning: 'bg-amber-500',
}

const statusLabel: Record<string, string> = {
  online: 'Online',
  offline: 'Offline',
  warning: 'Warning',
}

interface Props {
  data: AssetData
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

export function AssetOverviewWidget({ data, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Energy Assets</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Energy Assets</CardTitle>
        <span className="text-sm text-muted-foreground">{data.total.toLocaleString()} total</span>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading assets..." /></div>
        ) : data.categories.length === 0 ? (
          <EmptyState title="No asset data" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.categories.map((cat) => {
              const Icon = assetIcons[cat.icon] ?? Radio
              return (
                <div key={cat.label} className="rounded-lg border bg-card p-4 transition-shadow hover:shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className={cn(
                      'rounded-lg p-2',
                      cat.status === 'online' && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
                      cat.status === 'warning' && 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
                      cat.status === 'offline' && 'bg-red-500/10 text-red-600 dark:text-red-400',
                    )}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className={cn('h-2 w-2 rounded-full', statusDot[cat.status])} title={statusLabel[cat.status]} />
                  </div>
                  <p className="mt-3 text-2xl font-bold">{cat.count.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">{cat.label}</p>
                  <div className="mt-1 flex items-center gap-1 text-xs">
                    {cat.change > 0 ? (
                      <TrendingUp className="h-3 w-3 text-emerald-500" />
                    ) : cat.change < 0 ? (
                      <TrendingDown className="h-3 w-3 text-red-500" />
                    ) : null}
                    <span className={cn(
                      cat.change > 0 && 'text-emerald-500',
                      cat.change < 0 && 'text-red-500',
                    )}>
                      {cat.change > 0 ? '+' : ''}{cat.change}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
