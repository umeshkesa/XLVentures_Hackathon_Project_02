import { useAuth } from '@/store/auth'
import { useCustomerService } from '@/services/customerService'
import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const CUSTOMER_ID = 'C-1001'

export default function CustomerProfile() {
  const { user } = useAuth()
  const svc = useCustomerService()
  const [customer, setCustomer] = useState<{
    companyName: string
    industry: string
    location: string
    contactPerson: string
    contactEmail: string
    phone: string
    slaType: string
    contracts: { type: string; value: number; status: string; startDate: string; endDate: string }[]
    sla: { metric: string; target: number; actual: number; status: string }[]
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    svc.getById(CUSTOMER_ID).then((result) => {
      if (!result) return
      setCustomer({
        companyName: result.customer.companyName,
        industry: result.customer.industry,
        location: result.customer.location,
        contactPerson: result.customer.contactPerson,
        contactEmail: result.customer.contactEmail,
        phone: result.customer.phone,
        slaType: result.customer.slaType,
        contracts: result.contracts,
        sla: result.sla,
      })
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>
  if (!customer) return <div className="py-20 text-center text-muted-foreground">Customer data unavailable.</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground">Your account information</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs text-muted-foreground">Company</p>
              <p className="text-sm font-medium">{customer.companyName}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Industry</p>
              <p className="text-sm font-medium">{customer.industry}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Location</p>
              <p className="text-sm font-medium">{customer.location}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">SLA Type</p>
              <p className="text-sm font-medium">{customer.slaType}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Contact</p>
              <p className="text-sm font-medium">{customer.contactPerson}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Email</p>
              <p className="text-sm font-medium">{user?.email}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Phone</p>
              <p className="text-sm font-medium">{customer.phone}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contracts</CardTitle>
        </CardHeader>
        <CardContent>
          {customer.contracts.length === 0 ? (
            <p className="text-sm text-muted-foreground">No contracts available.</p>
          ) : (
            <div className="space-y-3">
              {customer.contracts.map((c, i) => (
                <div key={i} className="flex items-center justify-between rounded-md border p-3">
                  <div>
                    <p className="text-sm font-medium">{c.type}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(c.startDate).toLocaleDateString()} - {new Date(c.endDate).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">${c.value.toLocaleString()}</p>
                    <Badge variant={c.status === 'Active' ? 'default' : 'secondary'} className="text-[10px]">{c.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
