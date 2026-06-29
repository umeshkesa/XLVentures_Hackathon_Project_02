import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  Sun,
  Wind,
  Zap,
  BatteryCharging,
  Radio,

  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card, CardContent } from '@/components/Card'
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/Table'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorState } from '@/components/ErrorState'
import { EmptyState } from '@/components/EmptyState'
import { useAssetService } from '@/services/assetService'
import type { EnergyAsset, AssetType } from '@/types/assets'
import { cn } from '@/lib/utils'

const typeIcons: Record<AssetType, LucideIcon> = {
  SOLAR_PANEL: Sun,
  WIND_TURBINE: Wind,
  TRANSFORMER: Zap,
  BATTERY: BatteryCharging,
  SENSOR: Radio,
}

const typeLabels: Record<AssetType, string> = {
  SOLAR_PANEL: 'Solar Panels',
  WIND_TURBINE: 'Wind Turbines',
  TRANSFORMER: 'Transformers',
  BATTERY: 'Battery Storage',
  SENSOR: 'Sensors',
}

const statusLabel: Record<string, string> = {
  ACTIVE: 'Active',
  MAINTENANCE: 'Maintenance',
  ALERT: 'Alert',
  INACTIVE: 'Inactive',
  DECOMMISSIONED: 'Decommissioned',
}

const statusBadgeVariant: Record<string, 'success' | 'warning' | 'destructive' | 'secondary'> = {
  ACTIVE: 'success',
  MAINTENANCE: 'warning',
  ALERT: 'destructive',
  INACTIVE: 'secondary',
  DECOMMISSIONED: 'secondary',
}

export default function AssetsList() {
  const svc = useAssetService()
  const [assets, setAssets] = useState<EnergyAsset[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const limit = 15

  const load = () => {
    setLoading(true)
    svc.list({ type: typeFilter, status: statusFilter, search, page, limit }).then((res) => {
      setAssets(res.assets)
      setTotal(res.total)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load assets')
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const totalPages = Math.ceil(total / limit)

  const assetTypes: AssetType[] = ['SOLAR_PANEL', 'WIND_TURBINE', 'TRANSFORMER', 'BATTERY', 'SENSOR']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Energy Assets</h1>
        <p className="text-muted-foreground">{total} total assets</p>
      </div>

      {/* Asset type cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {assetTypes.map((type) => {
          const Icon = typeIcons[type]
          const count = assets.filter((a) => a.type === type).length
          return (
            <button
              key={type}
              onClick={() => { setTypeFilter(typeFilter === type ? '' : type); setPage(1) }}
              className={cn(
                'rounded-lg border p-4 text-left transition-all hover:shadow-md',
                typeFilter === type ? 'border-primary bg-primary/5' : 'bg-card',
              )}
            >
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-lg font-bold">{count}</p>
                  <p className="text-xs text-muted-foreground">{typeLabels[type]}</p>
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                className="h-10 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring"
                placeholder="Search assets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (load(), setPage(1))}
              />
            </div>
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
            >
              <option value="">All Status</option>
              <option value="ACTIVE">Active</option>
              <option value="MAINTENANCE">Maintenance</option>
              <option value="ALERT">Alert</option>
              <option value="INACTIVE">Inactive</option>
            </select>
            <Button variant="secondary" onClick={() => { load(); setPage(1) }}><Search className="h-4 w-4" /> Search</Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex justify-center py-16"><LoadingSpinner label="Loading assets..." /></div>
          ) : error ? (
            <div className="p-6"><ErrorState message={error} onRetry={load} /></div>
          ) : assets.length === 0 ? (
            <div className="p-6"><EmptyState title="No assets found" description="Try adjusting your filters." /></div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Health</TableHead>
                    <TableHead>Last Reading</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {assets.map((a) => {
                    const Icon = typeIcons[a.type]
                    return (
                      <TableRow key={a.id}>
                        <TableCell>
                          <Link to={`/assets/${a.id}`} className="flex items-center gap-3 hover:text-primary transition-colors">
                            <div className="rounded-lg bg-muted p-2">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div>
                              <p className="font-medium">{a.name}</p>
                              <p className="text-xs text-muted-foreground">{a.id}</p>
                            </div>
                          </Link>
                        </TableCell>
                        <TableCell className="text-sm">{typeLabels[a.type]}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">{a.location}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className={cn(
                              'h-2 w-16 rounded-full bg-muted overflow-hidden',
                            )}>
                              <div className={cn(
                                'h-full rounded-full',
                                a.healthScore >= 90 ? 'bg-emerald-500' : a.healthScore >= 75 ? 'bg-amber-500' : 'bg-red-500',
                              )} style={{ width: `${a.healthScore}%` }} />
                            </div>
                            <span className="text-xs text-muted-foreground">{a.healthScore}%</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {a.lastReading != null ? (
                            <span>{a.lastReading} {a.lastReadingUnit}</span>
                          ) : <span className="text-muted-foreground">—</span>}
                        </TableCell>
                        <TableCell>
                          <Badge variant={statusBadgeVariant[a.status]}>{statusLabel[a.status]}</Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" asChild>
                            <Link to={`/assets/${a.id}`}>View</Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between border-t px-6 py-4">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * limit + 1}–{Math.min(page * limit, total)} of {total}
                </p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</Button>
                  <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
                  <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
