import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Building2,
  FileText,
  CheckCircle2,
  AlertTriangle,
  MessageSquare,
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
import { useCustomerService } from '@/services/customerService'
import type { CustomerDetail as Detail } from '@/types/customers'
import { cn } from '@/lib/utils'

type Tab = 'profile' | 'contracts' | 'sla' | 'interactions'

const interactionIcons: Record<string, LucideIcon> = {
  email: Mail,
  phone: Phone,
  meeting: MessageSquare,
  support_ticket: FileText,
}

const slaStatusIcon: Record<string, LucideIcon> = {
  compliant: CheckCircle2,
  breached: AlertTriangle,
  at_risk: AlertTriangle,
}

const slaStatusColor: Record<string, string> = {
  compliant: 'text-emerald-500',
  breached: 'text-red-500',
  at_risk: 'text-amber-500',
}

export default function CustomerDetail() {
  const { id } = useParams<{ id: string }>()
  const svc = useCustomerService()
  const [data, setData] = useState<Detail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('profile')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    svc.getById(id).then((res) => {
      setData(res)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load customer')
      setLoading(false)
    })
  }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="flex justify-center py-16"><LoadingSpinner label="Loading customer..." /></div>
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!data) return <ErrorState title="Customer not found" message={`No customer with ID ${id}`} />

  const { customer, contracts, sla, interactions } = data

  const tabs: { key: Tab; label: string }[] = [
    { key: 'profile', label: 'Profile' },
    { key: 'contracts', label: `Contracts (${contracts.length})` },
    { key: 'sla', label: 'SLA' },
    { key: 'interactions', label: `Interactions (${interactions.length})` },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/customers"><ArrowLeft className="h-5 w-5" /></Link>
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{customer.companyName}</h1>
            <Badge variant={customer.status === 'Active' ? 'success' : customer.status === 'Inactive' ? 'secondary' : 'destructive'}>
              {customer.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">{customer.id}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={cn(
              'px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px',
              tab === t.key ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {tab === 'profile' && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Contact Information</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{customer.contactEmail}</span>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span>{customer.phone}</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span>{customer.location}</span>
              </div>
              <div className="flex items-center gap-3">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <span>{customer.industry}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Account Details</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Contact Person</span>
                <span className="font-medium">{customer.contactPerson}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">SLA Type</span>
                <Badge variant={customer.slaType === 'Premium' ? 'default' : 'secondary'}>{customer.slaType}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Contract Period</span>
                <span className="text-sm">{new Date(customer.contractStart).toLocaleDateString()} – {new Date(customer.contractEnd).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Open Cases</span>
                <span className="font-medium text-amber-500">{customer.openCases}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Total Cases</span>
                <span className="font-medium">{customer.totalCases}</span>
              </div>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader><CardTitle>Recent Interactions</CardTitle></CardHeader>
            <CardContent>
              {interactions.length === 0 ? (
                <EmptyState title="No interactions" />
              ) : (
                <div className="space-y-3">
                  {interactions.slice(0, 3).map((interaction) => {
                    const Icon = interactionIcons[interaction.type]
                    return (
                      <div key={interaction.id} className="flex items-center gap-3 rounded-lg border p-3">
                        {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
                        <div className="flex-1">
                          <p className="text-sm font-medium">{interaction.subject}</p>
                          <p className="text-xs text-muted-foreground">{interaction.agent} · {new Date(interaction.date).toLocaleDateString()}</p>
                        </div>
                        <Badge variant={interaction.status === 'resolved' ? 'success' : interaction.status === 'escalated' ? 'destructive' : 'warning'}>
                          {interaction.status}
                        </Badge>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Contracts Tab */}
      {tab === 'contracts' && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Contract</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Start Date</TableHead>
                  <TableHead>End Date</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contracts.map((ct) => (
                  <TableRow key={ct.id}>
                    <TableCell className="font-medium">{ct.id}</TableCell>
                    <TableCell>{ct.type}</TableCell>
                    <TableCell>{ct.startDate}</TableCell>
                    <TableCell>{ct.endDate}</TableCell>
                    <TableCell>${ct.value.toLocaleString()}</TableCell>
                    <TableCell><Badge variant={ct.status === 'Active' ? 'success' : ct.status === 'Expired' ? 'secondary' : 'warning'}>{ct.status}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* SLA Tab */}
      {tab === 'sla' && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sla.map((entry) => {
            const Icon = slaStatusIcon[entry.status]
            return (
              <Card key={entry.metric}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">{entry.metric}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    {Icon && <Icon className={cn('h-5 w-5', slaStatusColor[entry.status])} />}
                    <span className={cn('text-lg font-bold', slaStatusColor[entry.status])}>
                      {entry.status === 'compliant' ? 'Compliant' : entry.status === 'breached' ? 'Breached' : 'At Risk'}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                    <span>Target: {entry.target}{entry.metric.includes('%') ? '%' : entry.metric.includes('min') ? 'min' : ''}</span>
                    <span>Actual: {entry.actual}{entry.metric.includes('%') ? '%' : entry.metric.includes('min') ? 'min' : ''}</span>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Interactions Tab */}
      {tab === 'interactions' && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Agent</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {interactions.map((interaction) => {
                  const Icon = interactionIcons[interaction.type]
                  return (
                    <TableRow key={interaction.id}>
                      <TableCell className="text-sm text-muted-foreground">{new Date(interaction.date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
                          <span className="capitalize">{interaction.type.replace('_', ' ')}</span>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{interaction.subject}</TableCell>
                      <TableCell>{interaction.agent}</TableCell>
                      <TableCell><Badge variant={interaction.status === 'resolved' ? 'success' : interaction.status === 'escalated' ? 'destructive' : 'warning'}>{interaction.status}</Badge></TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
