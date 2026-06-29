import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Sun,
  Wind,
  Zap,
  BatteryCharging,
  Radio,
  AlertTriangle,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/Table'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorState } from '@/components/ErrorState'
import { EmptyState } from '@/components/EmptyState'
import { useAssetService } from '@/services/assetService'
import type { AssetDetail as Detail, AssetType } from '@/types/assets'
import { cn } from '@/lib/utils'

type Tab = 'overview' | 'maintenance' | 'alerts' | 'recommendations'

const typeIcons: Record<AssetType, LucideIcon> = {
  SOLAR_PANEL: Sun,
  WIND_TURBINE: Wind,
  TRANSFORMER: Zap,
  BATTERY: BatteryCharging,
  SENSOR: Radio,
}

const typeLabels: Record<AssetType, string> = {
  SOLAR_PANEL: 'Solar Panel',
  WIND_TURBINE: 'Wind Turbine',
  TRANSFORMER: 'Transformer',
  BATTERY: 'Battery Storage',
  SENSOR: 'Sensor',
}

const statusLabel: Record<string, string> = {
  ACTIVE: 'Active', MAINTENANCE: 'Maintenance', ALERT: 'Alert', INACTIVE: 'Inactive', DECOMMISSIONED: 'Decommissioned',
}

const statusBadge: Record<string, 'success' | 'warning' | 'destructive' | 'secondary'> = {
  ACTIVE: 'success', MAINTENANCE: 'warning', ALERT: 'destructive', INACTIVE: 'secondary', DECOMMISSIONED: 'secondary',
}

const alertSeverityIcon: Record<string, LucideIcon> = { critical: AlertTriangle, warning: AlertTriangle, info: AlertTriangle }
const alertSeverityColor: Record<string, string> = { critical: 'text-red-500 bg-red-500/10', warning: 'text-amber-500 bg-amber-500/10', info: 'text-blue-500 bg-blue-500/10' }

const priorityBadge: Record<string, 'destructive' | 'warning' | 'default' | 'secondary'> = {
  critical: 'destructive', high: 'warning', medium: 'default', low: 'secondary',
}

export default function AssetDetail() {
  const { id } = useParams<{ id: string }>()
  const svc = useAssetService()
  const [data, setData] = useState<Detail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('overview')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    svc.getById(id).then((res) => {
      setData(res)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load asset')
      setLoading(false)
    })
  }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="flex justify-center py-16"><LoadingSpinner label="Loading asset..." /></div>
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!data) return <ErrorState title="Asset not found" message={`No asset with ID ${id}`} />

  const { asset, readings, maintenance, alerts, recommendations } = data
  const Icon = typeIcons[asset.type]

  const tabs: { key: Tab; label: string; count?: number }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'maintenance', label: 'Maintenance', count: maintenance.length },
    { key: 'alerts', label: 'Alerts', count: alerts.length },
    { key: 'recommendations', label: 'Recommendations', count: recommendations.length },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/assets"><ArrowLeft className="h-5 w-5" /></Link>
        </Button>
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
            <Icon className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight">{asset.name}</h1>
              <Badge variant={statusBadge[asset.status]}>{statusLabel[asset.status]}</Badge>
            </div>
            <p className="text-muted-foreground">{asset.id} · {typeLabels[asset.type]} · {asset.location}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={cn(
              'px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px',
              tab === t.key ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground',
            )}
          >
            {t.label}{t.count != null ? ` (${t.count})` : ''}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {tab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Asset Details</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-xs text-muted-foreground">Manufacturer</p><p className="font-medium">{asset.manufacturer}</p></div>
                <div><p className="text-xs text-muted-foreground">Model</p><p className="font-medium">{asset.model}</p></div>
                <div><p className="text-xs text-muted-foreground">Rated Capacity</p><p className="font-medium">{asset.ratedCapacity} kW</p></div>
                <div><p className="text-xs text-muted-foreground">Installation Date</p><p className="font-medium">{new Date(asset.installationDate).toLocaleDateString()}</p></div>
                <div><p className="text-xs text-muted-foreground">Readings Collected</p><p className="font-medium">{asset.readingCount.toLocaleString()}</p></div>
                <div><p className="text-xs text-muted-foreground">Last Reading</p><p className="font-medium">{asset.lastReading ?? '—'} {asset.lastReadingUnit}</p></div>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-2">Tags</p>
                <div className="flex flex-wrap gap-1.5">
                  {asset.tags.map((tag) => <Badge key={tag} variant="secondary">{tag}</Badge>)}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Health Score</CardTitle></CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-6">
              <div className="relative flex h-36 w-36 items-center justify-center">
                <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" className="text-muted" strokeWidth="8" />
                  <circle cx="60" cy="60" r="52" fill="none"
                    stroke={asset.healthScore >= 90 ? '#10b981' : asset.healthScore >= 75 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8" strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 52}`}
                    strokeDashoffset={`${2 * Math.PI * 52 * (1 - asset.healthScore / 100)}`}
                  />
                </svg>
                <span className={cn(
                  'absolute text-3xl font-bold',
                  asset.healthScore >= 90 ? 'text-emerald-500' : asset.healthScore >= 75 ? 'text-amber-500' : 'text-red-500',
                )}>{asset.healthScore}%</span>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader><CardTitle>Recent Readings (24h)</CardTitle></CardHeader>
            <CardContent>
              {readings.length === 0 ? (
                <EmptyState title="No readings" />
              ) : (
                <div className="h-48">
                  <svg className="h-full w-full" viewBox="0 0 240 80" preserveAspectRatio="none">
                    <polyline
                      fill="none" stroke="var(--primary)" strokeWidth="2"
                      points={readings.map((r, i) => `${(i / Math.max(readings.length - 1, 1)) * 240},${80 - (r.value / Math.max(...readings.map((x) => x.value))) * 70}`).join(' ')}
                    />
                  </svg>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Maintenance Tab */}
      {tab === 'maintenance' && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow><TableHead>Date</TableHead><TableHead>Type</TableHead><TableHead>Description</TableHead><TableHead>Technician</TableHead><TableHead>Duration</TableHead><TableHead>Status</TableHead></TableRow>
              </TableHeader>
              <TableBody>
                {maintenance.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="text-sm text-muted-foreground">{new Date(m.date).toLocaleDateString()}</TableCell>
                    <TableCell className="font-medium">{m.type}</TableCell>
                    <TableCell className="text-sm">{m.description}</TableCell>
                    <TableCell>{m.technician}</TableCell>
                    <TableCell>{m.durationHours}h</TableCell>
                    <TableCell><Badge variant={m.status === 'completed' ? 'success' : m.status === 'in_progress' ? 'warning' : m.status === 'scheduled' ? 'default' : 'secondary'}>{m.status.replace('_', ' ')}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Alerts Tab */}
      {tab === 'alerts' && (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const AlertIcon = alertSeverityIcon[alert.severity]
            return (
              <Card key={alert.id} className={cn(
                alert.severity === 'critical' && 'border-red-500/20',
                alert.severity === 'warning' && 'border-amber-500/20',
              )}>
                <CardContent className="flex items-start gap-4 p-4">
                  <div className={cn('flex h-10 w-10 items-center justify-center rounded-full', alertSeverityColor[alert.severity])}>
                    <AlertIcon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{alert.title}</p>
                      <Badge variant={alert.severity === 'critical' ? 'destructive' : 'warning'}>{alert.severity}</Badge>
                      {!alert.acknowledged && <span className="h-2 w-2 rounded-full bg-red-500" />}
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.description}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{new Date(alert.timestamp).toLocaleString()}</p>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Recommendations Tab */}
      {tab === 'recommendations' && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow><TableHead>Date</TableHead><TableHead>Title</TableHead><TableHead>Priority</TableHead><TableHead>Status</TableHead></TableRow>
              </TableHeader>
              <TableBody>
                {recommendations.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="text-sm text-muted-foreground">{new Date(r.createdAt).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <p className="font-medium">{r.title}</p>
                      <p className="text-xs text-muted-foreground">{r.description}</p>
                    </TableCell>
                    <TableCell><Badge variant={priorityBadge[r.priority]}>{r.priority}</Badge></TableCell>
                    <TableCell><Badge variant={r.status === 'implemented' ? 'success' : r.status === 'rejected' ? 'secondary' : 'default'}>{r.status}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
