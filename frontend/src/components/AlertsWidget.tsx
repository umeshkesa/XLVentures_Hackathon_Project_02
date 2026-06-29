import { cn } from '@/lib/utils'
import {
  AlertTriangle,
  ShieldAlert,
  Info,
  ThumbsUp,
  Upload,
  HardDrive,
  FileWarning,
} from 'lucide-react'
import { Badge } from './Badge'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import { EmptyState } from './EmptyState'
import type { AlertItem } from '@/types/dashboard'

const typeIcons = {
  critical: ShieldAlert,
  warning: AlertTriangle,
  info: Info,
}

const typeColors = {
  critical: 'text-red-500 bg-red-500/10',
  warning: 'text-amber-500 bg-amber-500/10',
  info: 'text-blue-500 bg-blue-500/10',
}

const badgeVariant: Record<string, 'destructive' | 'warning' | 'default' | 'success' | 'secondary' | 'outline'> = {
  critical: 'destructive',
  warning: 'warning',
  info: 'default',
}

const sourceIcons: Record<string, typeof ThumbsUp> = {
  recommendation: ThumbsUp,
  import: Upload,
  asset: HardDrive,
  compliance: FileWarning,
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

interface Props {
  items: AlertItem[]
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

export function AlertsWidget({ items, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Alerts</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  const critical = items.filter((a) => a.type === 'critical').length

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Alerts</CardTitle>
        {critical > 0 && (
          <Badge variant="destructive">{critical} critical</Badge>
        )}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading alerts..." /></div>
        ) : items.length === 0 ? (
          <EmptyState title="No alerts" description="All systems operational." />
        ) : (
          <div className="space-y-3">
            {items.map((alert) => {
              const Icon = typeIcons[alert.type]
              const SourceIcon = sourceIcons[alert.source]
              return (
                <div
                  key={alert.id}
                  className={cn(
                    'flex gap-3 rounded-lg border p-3 transition-colors',
                    alert.type === 'critical' && 'border-red-500/20 bg-red-500/5',
                    alert.type === 'warning' && 'border-amber-500/20 bg-amber-500/5',
                    alert.type === 'info' && 'border-transparent bg-muted/30',
                  )}
                >
                  <div className={cn('flex h-9 w-9 shrink-0 items-center justify-center rounded-full', typeColors[alert.type])}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{alert.title}</p>
                      <Badge variant={badgeVariant[alert.type]}>
                        {alert.type}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{alert.description}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground/60">
                      <span>{timeAgo(alert.timestamp)}</span>
                      {SourceIcon && <SourceIcon className="h-3 w-3" />}
                    </div>
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
