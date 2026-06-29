import { useEffect, useState } from 'react'
import { useInteractionService } from '@/services/interactionService'
import { useEvidenceFrontendService } from '@/services/evidenceFrontendService'
import { useRecommendationService } from '@/services/recommendationFrontendService'
import { useCustomerService } from '@/services/customerService'
import { useKnowledgeService } from '@/services/knowledgeFrontendService'
import { useAuth } from '@/store/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Link } from 'react-router-dom'

const CUSTOMER_ID = 'C-1001'

export default function CustomerDashboard() {
  const { user } = useAuth()
  const intSvc = useInteractionService()
  const evSvc = useEvidenceFrontendService()
  const recSvc = useRecommendationService()
  const custSvc = useCustomerService()
  const knSvc = useKnowledgeService()

  const [loading, setLoading] = useState(true)
  const [openRequests, setOpenRequests] = useState(0)
  const [criticalAlerts, setCriticalAlerts] = useState(0)
  const [recentRecs, setRecentRecs] = useState<{ id: string; title: string; priority: string; status: string }[]>([])
  const [recentInteractions, setRecentInteractions] = useState<{ id: string; subject: string; type: string; date: string }[]>([])
  const [evidenceCount, setEvidenceCount] = useState(0)
  const [customerDetail, setCustomerDetail] = useState<{ sla: { metric: string; target: number; actual: number; status: string }[] } | null>(null)
  const [upcomingMaintenance, setUpcomingMaintenance] = useState(0)
  const [knowledgeCount, setKnowledgeCount] = useState(0)

  useEffect(() => {
    const load = async () => {
      try {
        const [interactions, evidence, recs, customer, knowledge] = await Promise.all([
          intSvc.list({ customerId: CUSTOMER_ID, page: 1, limit: 100 }),
          evSvc.list({ page: 1, limit: 100 }),
          recSvc.list({ page: 1, limit: 100 }),
          custSvc.getById(CUSTOMER_ID),
          knSvc.list({ page: 1, limit: 100 }),
        ])

        setOpenRequests(interactions.items.filter((i) => i.status === 'pending' || i.status === 'escalated').length)

        const c1Evidence = evidence.items.filter((e) => e.relatedCustomers.includes(CUSTOMER_ID))
        setEvidenceCount(c1Evidence.length)
        setCriticalAlerts(c1Evidence.filter((e) => e.severity === 'critical').length)

        const c1Recs = recs.items.filter((r) => r.customerIds.includes(CUSTOMER_ID))
        setRecentRecs(
          c1Recs
            .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
            .slice(0, 5)
            .map((r) => ({ id: r.id, title: r.title, priority: r.priority, status: r.status })),
        )

        setRecentInteractions(
          interactions.items
            .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
            .slice(0, 5)
            .map((i) => ({ id: i.id, subject: i.subject, type: i.type, date: i.date })),
        )

        if (customer) setCustomerDetail({ sla: customer.sla })

        setKnowledgeCount(knowledge.items.length)

        const c1Assets = [...new Set([
          ...interactions.items.flatMap((i) => i.relatedAssets),
          ...c1Evidence.flatMap((e) => e.relatedAssets),
        ])]
        setUpcomingMaintenance(Math.min(c1Assets.length, 3))
      } catch {
        // silent
      } finally {
        setLoading(false)
      }
    }
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const slaCompliant = customerDetail?.sla.filter((s) => s.status === 'compliant').length ?? 0
  const slaTotal = customerDetail?.sla.length ?? 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Welcome, {user?.customerName ?? 'Customer'}</h1>
        <p className="text-muted-foreground">Your energy intelligence dashboard</p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Open Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{openRequests}</div>
            <Link to="/customer/support" className="mt-1 inline-block text-xs text-primary hover:underline">
              View support tickets
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Critical Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-destructive">{criticalAlerts}</div>
            <Link to="/customer/evidence" className="mt-1 inline-block text-xs text-primary hover:underline">
              View evidence
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Evidence Generated</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{evidenceCount}</div>
            <Link to="/customer/evidence" className="mt-1 inline-block text-xs text-primary hover:underline">
              View all evidence
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">SLA Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{slaCompliant}/{slaTotal}</div>
            <span className="mt-1 inline-block text-xs text-muted-foreground">
              Compliance metrics
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Recent Interactions + Latest Recommendations */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Interactions</CardTitle>
          </CardHeader>
          <CardContent>
            {recentInteractions.length === 0 ? (
              <EmptyState title="No interactions" description="No recent customer interactions" />
            ) : (
              <div className="space-y-3">
                {recentInteractions.map((i) => (
                  <Link
                    key={i.id}
                    to={`/customer/interactions?id=${i.id}`}
                    className="flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-accent"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{i.subject}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge variant="outline" className="text-[10px] capitalize">{i.type.replace('_', ' ')}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(i.date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
            <Link to="/customer/interactions" className="mt-3 inline-block text-sm text-primary hover:underline">
              View all interactions
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Latest Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            {recentRecs.length === 0 ? (
              <EmptyState title="No recommendations" description="No recommendations available" />
            ) : (
              <div className="space-y-3">
                {recentRecs.map((r) => (
                  <Link
                    key={r.id}
                    to={`/customer/recommendations?id=${r.id}`}
                    className="flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-accent"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{r.title}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge variant={r.priority === 'critical' || r.priority === 'high' ? 'destructive' : r.priority === 'medium' ? 'default' : 'secondary'} className="text-[10px]">{r.priority}</Badge>
                        <Badge variant="outline" className="text-[10px]">{r.status}</Badge>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
            <Link to="/customer/recommendations" className="mt-3 inline-block text-sm text-primary hover:underline">
              View all recommendations
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Upcoming Maintenance + Knowledge + SLA */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Upcoming Maintenance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{upcomingMaintenance}</div>
            <p className="mt-1 text-sm text-muted-foreground">Tasks requiring attention</p>
            <Link to="/customer/assets" className="mt-3 inline-block text-sm text-primary hover:underline">
              View my assets
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Knowledge Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{knowledgeCount}</div>
            <p className="mt-1 text-sm text-muted-foreground">Available documents</p>
            <Link to="/customer/knowledge" className="mt-3 inline-block text-sm text-primary hover:underline">
              Browse knowledge base
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">SLA Compliance</CardTitle>
          </CardHeader>
          <CardContent>
            {customerDetail?.sla.length ? (
              <div className="space-y-2">
                {customerDetail.sla.map((s) => (
                  <div key={s.metric} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{s.metric}</span>
                    <Badge variant={s.status === 'compliant' ? 'default' : s.status === 'at_risk' ? 'secondary' : 'destructive'} className="text-[10px]">
                      {s.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No SLA data" description="SLA information unavailable" />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
