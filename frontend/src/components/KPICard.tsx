import { cn } from '@/lib/utils'
import {
  Users,
  HardDrive,
  ThumbsUp,
  ClipboardCheck,
  AlertTriangle,
  Upload,
  BookOpen,
  Activity,
  type LucideIcon,
} from 'lucide-react'
import { Card, CardContent } from './Card'
import type { KPI } from '@/types/dashboard'

const kpiIcons: Record<string, LucideIcon> = {
  Users,
  HardDrive,
  ThumbsUp,
  ClipboardCheck,
  AlertTriangle,
  Upload,
  BookOpen,
  Activity,
}

interface KPICardProps {
  kpi: KPI
}

export function KPICard({ kpi }: KPICardProps) {
  const Icon = kpiIcons[kpi.icon] ?? Activity

  return (
    <Card hover>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{kpi.label}</p>
            <p className="text-2xl font-bold tracking-tight">{kpi.formatted}</p>
          </div>
          <div className={cn(
            'rounded-lg p-2.5',
            kpi.trend === 'up' && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
            kpi.trend === 'down' && 'bg-red-500/10 text-red-600 dark:text-red-400',
            kpi.trend === 'neutral' && 'bg-muted text-muted-foreground',
          )}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center gap-1 text-xs">
          <span className={cn(
            'font-medium',
            kpi.change > 0 && 'text-emerald-600 dark:text-emerald-400',
            kpi.change < 0 && 'text-red-600 dark:text-red-400',
          )}>
            {kpi.change > 0 ? '+' : ''}{kpi.change}%
          </span>
          <span className="text-muted-foreground">{kpi.changeLabel}</span>
        </div>
      </CardContent>
    </Card>
  )
}

export function KPICardSkeleton() {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="h-4 w-24 animate-pulse rounded bg-muted" />
        <div className="mt-2 h-8 w-20 animate-pulse rounded bg-muted" />
        <div className="mt-3 flex gap-1">
          <div className="h-3 w-10 animate-pulse rounded bg-muted" />
          <div className="h-3 w-28 animate-pulse rounded bg-muted" />
        </div>
      </CardContent>
    </Card>
  )
}
