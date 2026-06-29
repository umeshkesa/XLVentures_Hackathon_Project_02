import { useEffect, useState } from 'react'
import { useInteractionService } from '@/services/interactionService'
import { useEvidenceFrontendService } from '@/services/evidenceFrontendService'
import { useAssetService } from '@/services/assetService'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const CUSTOMER_ID = 'C-1001'

const typeLabels: Record<string, string> = {
  SOLAR_PANEL: 'Solar Panel',
  WIND_TURBINE: 'Wind Turbine',
  TRANSFORMER: 'Transformer',
  BATTERY: 'Battery',
  SENSOR: 'Sensor',
}

export default function CustomerAssets() {
  const intSvc = useInteractionService()
  const evSvc = useEvidenceFrontendService()
  const assetSvc = useAssetService()

  const [assets, setAssets] = useState<{ id: string; name: string; type: string; status: string; healthScore: number; location: string }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [interactions, evidence] = await Promise.all([
          intSvc.list({ customerId: CUSTOMER_ID, page: 1, limit: 100 }),
          evSvc.list({ page: 1, limit: 100 }),
        ])
        const ids = [...new Set([
          ...interactions.items.flatMap((i) => i.relatedAssets),
          ...evidence.items.filter((e) => e.relatedCustomers.includes(CUSTOMER_ID)).flatMap((e) => e.relatedAssets),
        ])]

        const allAssets = await assetSvc.list({ page: 1, limit: 200 })
        const filtered = allAssets.assets.filter((a) => ids.includes(a.id))
        setAssets(filtered.map((a) => ({ id: a.id, name: a.name, type: a.type, status: a.status, healthScore: a.healthScore, location: a.location })))
      } catch {
        // silent
      } finally {
        setLoading(false)
      }
    }
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Assets</h1>
        <p className="text-muted-foreground">{assets.length} assets associated with your account</p>
      </div>

      {assets.length === 0 ? (
        <EmptyState title="No assets" description="No assets are currently associated with your account." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {assets.map((a) => (
            <Link key={a.id} to={`/assets/${a.id}`}>
              <Card className="transition-colors hover:bg-accent cursor-pointer">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm">{a.name}</CardTitle>
                    <Badge variant={a.status === 'ACTIVE' ? 'default' : a.status === 'ALERT' ? 'destructive' : 'secondary'} className="text-[10px]">
                      {a.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <p>Type: {typeLabels[a.type] ?? a.type}</p>
                    <p>Location: {a.location}</p>
                    <div className="flex items-center gap-2">
                      <span>Health:</span>
                      <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${a.healthScore}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium">{a.healthScore}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
