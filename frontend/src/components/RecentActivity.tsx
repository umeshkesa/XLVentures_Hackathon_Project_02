import { cn } from '@/lib/utils'
import {
  Upload,
  FileSearch,
  ThumbsUp,
  ClipboardCheck,
  Zap,
  Clock,
  CheckCircle2,
  XCircle,
  type LucideIcon,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import type { ActivityItem } from '@/types/dashboard'

const typeConfig: Record<string, { icon: LucideIcon; color: string }> = {
  import: { icon: Upload, color: 'text-blue-500 bg-blue-500/10' },
  evidence: { icon: FileSearch, color: 'text-violet-500 bg-violet-500/10' },
  recommendation: { icon: ThumbsUp, color: 'text-emerald-500 bg-emerald-500/10' },
  review: { icon: ClipboardCheck, color: 'text-amber-500 bg-amber-500/10' },
  action: { icon: Zap, color: 'text-cyan-500 bg-cyan-500/10' },
}

const statusIcon: Record<string, LucideIcon> = {
  completed: CheckCircle2,
  pending: Clock,
  failed: XCircle,
}

const statusColor: Record<string, string> = {
  completed: 'text-emerald-500',
  pending: 'text-amber-500',
  failed: 'text-red-500',
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

interface RecentActivityProps {
  items: ActivityItem[]
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

export function RecentActivity({ items, loading, error, onRetry }: RecentActivityProps) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading activity..." /></div>
        ) : items.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No recent activity</p>
        ) : (
          <div className="space-y-0">
            {items.map((item, i) => {
              const cfg = typeConfig[item.type] ?? typeConfig.import
              const Icon = cfg.icon
              const StatusIcon = statusIcon[item.status]
              return (
                <div key={item.id} className={cn(
                  'relative flex gap-4 pb-6',
                  i < items.length - 1 && '',
                )}>
                  {i < items.length - 1 && (
                    <div className="absolute left-[19px] top-10 bottom-0 w-px bg-border" />
                  )}
                  <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-full', cfg.color)}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{item.title}</p>
                      {StatusIcon && (
                        <StatusIcon className={cn('h-3.5 w-3.5 shrink-0', statusColor[item.status])} />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                    <p className="text-xs text-muted-foreground/60">{timeAgo(item.timestamp)}</p>
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
