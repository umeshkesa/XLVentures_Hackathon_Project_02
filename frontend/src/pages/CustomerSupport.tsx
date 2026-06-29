import { useEffect, useState } from 'react'
import { useInteractionService } from '@/services/interactionService'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const CUSTOMER_ID = 'C-1001'

const requestTypes = new Set(['service_request', 'complaint'])

export default function CustomerSupport() {
  const svc = useInteractionService()
  const [requests, setRequests] = useState<{ id: string; type: string; subject: string; date: string; status: string; content: string }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    svc.list({ customerId: CUSTOMER_ID, page: 1, limit: 100 }).then((res) => {
      setRequests(
        res.items
          .filter((i) => requestTypes.has(i.type))
          .map((i) => ({ id: i.id, type: i.type, subject: i.subject, date: i.date, status: i.status, content: i.content })),
      )
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const openCount = requests.filter((r) => r.status === 'pending' || r.status === 'escalated').length
  const resolvedCount = requests.filter((r) => r.status === 'resolved').length

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Support</h1>
        <p className="text-muted-foreground">Service requests and complaints</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{requests.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Open</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-500">{openCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Resolved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{resolvedCount}</div>
          </CardContent>
        </Card>
      </div>

      {requests.length === 0 ? (
        <EmptyState title="No support requests" description="You have no support requests or complaints." />
      ) : (
        <div className="space-y-3">
          {requests.map((r) => (
            <div key={r.id} className="rounded-md border bg-card p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px] capitalize">{r.type.replace(/_/g, ' ')}</Badge>
                    <p className="text-sm font-medium">{r.subject}</p>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{r.content}</p>
                  <p className="mt-1 text-[10px] text-muted-foreground">{new Date(r.date).toLocaleString()}</p>
                </div>
                <Badge variant={r.status === 'resolved' ? 'default' : r.status === 'pending' ? 'secondary' : 'destructive'} className="shrink-0 text-[10px]">
                  {r.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
