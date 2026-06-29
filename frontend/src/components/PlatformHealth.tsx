import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import type { PlatformHealth as HealthData } from '@/types/dashboard'

const statusDot: Record<string, string> = {
  healthy: 'bg-emerald-500',
  degraded: 'bg-amber-500',
  down: 'bg-red-500',
  unknown: 'bg-muted-foreground/40',
}

const statusLabel: Record<string, string> = {
  healthy: 'Healthy',
  degraded: 'Degraded',
  down: 'Down',
  unknown: 'Unknown',
}

interface PlatformHealthProps {
  health: HealthData
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

export function PlatformHealthWidget({ health, loading, error, onRetry }: PlatformHealthProps) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Platform Health</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  const entries = Object.values(health)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Platform Health</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading health..." /></div>
        ) : (
          <div className="space-y-3">
            {entries.map((s) => (
              <div key={s.label} className="flex items-center justify-between rounded-lg bg-muted/50 px-3 py-2.5">
                <div className="flex items-center gap-2.5">
                  <span className={cn('h-2.5 w-2.5 rounded-full', statusDot[s.status])} />
                  <span className="text-sm font-medium">{s.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {s.latency !== undefined && (
                    <span className="text-xs text-muted-foreground">{s.latency}ms</span>
                  )}
                  <span className={cn(
                    'text-xs font-medium',
                    s.status === 'healthy' && 'text-emerald-500',
                    s.status === 'degraded' && 'text-amber-500',
                    s.status === 'down' && 'text-red-500',
                    s.status === 'unknown' && 'text-muted-foreground',
                  )}>
                    {statusLabel[s.status]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
