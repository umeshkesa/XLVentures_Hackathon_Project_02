import { useEffect, useState } from 'react'
import { useRecommendationService } from '@/services/recommendationFrontendService'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Modal } from '@/components/Modal'

const CUSTOMER_ID = 'C-1001'

export default function CustomerRecommendations() {
  const svc = useRecommendationService()
  const [items, setItems] = useState<{ id: string; title: string; description: string; priority: string; status: string; confidence: number; estimatedCost: number; estimatedSavings: number; createdAt: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    svc.list({ page: 1, limit: 100 }).then((res) => {
      setItems(
        res.items
          .filter((r) => r.customerIds.includes(CUSTOMER_ID))
          .map((r) => ({ id: r.id, title: r.title, description: r.description, priority: r.priority, status: r.status, confidence: r.confidence, estimatedCost: r.estimatedCost, estimatedSavings: r.estimatedSavings, createdAt: r.createdAt })),
      )
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const selectedItem = items.find((i) => i.id === selected)

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Recommendations</h1>
        <p className="text-muted-foreground">{items.length} recommendations for your account</p>
      </div>

      {items.length === 0 ? (
        <EmptyState title="No recommendations" description="No recommendations are currently available for your account." />
      ) : (
        <div className="space-y-3">
          {items.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => setSelected(r.id)}
              className="w-full rounded-md border bg-card p-4 text-left transition-colors hover:bg-accent"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{r.title}</p>
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{r.description}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span>Cost: ${r.estimatedCost.toLocaleString()}</span>
                    <span>Savings: ${r.estimatedSavings.toLocaleString()}</span>
                    <span>Confidence: {Math.round(r.confidence * 100)}%</span>
                    <span>{new Date(r.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                  <Badge variant={r.priority === 'critical' || r.priority === 'high' ? 'destructive' : r.priority === 'medium' ? 'default' : 'secondary'} className="text-[10px]">
                    {r.priority}
                  </Badge>
                  <Badge variant="outline" className="text-[10px]">{r.status}</Badge>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      <Modal open={!!selectedItem} onOpenChange={(open) => { if (!open) setSelected(null) }} title={selectedItem?.title ?? ''}>
        {selectedItem && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant={selectedItem.priority === 'critical' || selectedItem.priority === 'high' ? 'destructive' : 'default'} className="text-xs">
                {selectedItem.priority}
              </Badge>
              <Badge variant="outline" className="text-xs">{selectedItem.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{selectedItem.description}</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md bg-muted p-3">
                <p className="text-xs text-muted-foreground">Estimated Cost</p>
                <p className="text-lg font-bold">${selectedItem.estimatedCost.toLocaleString()}</p>
              </div>
              <div className="rounded-md bg-muted p-3">
                <p className="text-xs text-muted-foreground">Estimated Savings</p>
                <p className="text-lg font-bold text-green-600">${selectedItem.estimatedSavings.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>Confidence: {Math.round(selectedItem.confidence * 100)}%</span>
              <span>Created: {new Date(selectedItem.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
