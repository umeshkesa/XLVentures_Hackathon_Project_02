import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Users,
  Building2,
  MapPin,
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
import { useCustomerService } from '@/services/customerService'
import type { Customer } from '@/types/customers'

const statusBadge: Record<string, 'success' | 'secondary' | 'destructive'> = {
  Active: 'success',
  Inactive: 'secondary',
  Suspended: 'destructive',
}

const industries = ['', 'Energy', 'Utilities', 'Manufacturing', 'Technology', 'Infrastructure']

export default function CustomersList() {
  const svc = useCustomerService()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [industry, setIndustry] = useState('')
  const [status, setStatus] = useState('')
  const limit = 12

  const load = () => {
    setLoading(true)
    setError(null)
    svc.list({ search, industry, status, page, limit }).then((res) => {
      setCustomers(res.customers)
      setTotal(res.total)
      setLoading(false)
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load customers')
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [page]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearch = () => { setPage(1); load() }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Customers</h1>
          <p className="text-muted-foreground">{total} total customers</p>
        </div>
        <Button><Users className="h-4 w-4" /> Add Customer</Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                className="h-10 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring"
                placeholder="Search customers..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
              value={industry}
              onChange={(e) => { setIndustry(e.target.value); setPage(1); }}
            >
              <option value="">All Industries</option>
              {industries.filter(Boolean).map((ind) => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring"
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            >
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Suspended">Suspended</option>
            </select>
            <Button variant="secondary" onClick={handleSearch}><Search className="h-4 w-4" /> Search</Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex justify-center py-16"><LoadingSpinner label="Loading customers..." /></div>
          ) : error ? (
            <div className="p-6"><ErrorState message={error} onRetry={load} /></div>
          ) : customers.length === 0 ? (
            <div className="p-6"><EmptyState title="No customers found" description="Try adjusting your search or filters." /></div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Company</TableHead>
                    <TableHead>Industry</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>SLA</TableHead>
                    <TableHead>Cases</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {customers.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>
                        <Link to={`/customers/${c.id}`} className="flex items-center gap-3 hover:text-primary transition-colors">
                          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary text-sm font-medium">
                            {c.companyName.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium">{c.companyName}</p>
                            <p className="text-xs text-muted-foreground">{c.id}</p>
                          </div>
                        </Link>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Building2 className="h-4 w-4 text-muted-foreground" />
                          {c.industry}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          {c.location}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={c.slaType === 'Premium' ? 'default' : c.slaType === 'Enterprise' ? 'success' : 'secondary'}>
                          {c.slaType}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <span className="font-medium">{c.openCases}</span>
                          <span className="text-muted-foreground"> / {c.totalCases}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusBadge[c.status]}>{c.status}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/customers/${c.id}`}>View</Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between border-t px-6 py-4">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * limit + 1}–{Math.min(page * limit, total)} of {total}
                </p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const start = Math.max(1, page - 2)
                    const p = start + i
                    if (p > totalPages) return null
                    return (
                      <Button key={p} variant={p === page ? 'default' : 'outline'} size="sm" onClick={() => setPage(p)}>
                        {p}
                      </Button>
                    )
                  })}
                  <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
