import { Users, Briefcase, FileText, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorState } from './ErrorState'
import { EmptyState } from './EmptyState'
import type { CustomerSummary as CustomerData } from '@/types/dashboard'

interface Props {
  data: CustomerData
  loading?: boolean
  error?: string | null
  onRetry?: () => void
}

export function CustomerSummaryWidget({ data, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <Card>
        <CardHeader><CardTitle>Customer Summary</CardTitle></CardHeader>
        <CardContent>
          <ErrorState message={error} onRetry={onRetry} />
        </CardContent>
      </Card>
    )
  }

  const slaPercent = data.slaTotal > 0 ? Math.round((data.slaCompliant / data.slaTotal) * 100) : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Customer Summary</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8"><LoadingSpinner label="Loading customers..." /></div>
        ) : data.totalCustomers === 0 ? (
          <EmptyState title="No customer data" />
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1 rounded-lg bg-muted/50 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Users className="h-4 w-4" />
                <span className="text-xs font-medium">Customers</span>
              </div>
              <p className="text-2xl font-bold">{data.totalCustomers.toLocaleString()}</p>
            </div>
            <div className="space-y-1 rounded-lg bg-muted/50 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Briefcase className="h-4 w-4" />
                <span className="text-xs font-medium">Active Cases</span>
              </div>
              <p className="text-2xl font-bold">{data.activeCases.toLocaleString()}</p>
            </div>
            <div className="space-y-1 rounded-lg bg-muted/50 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span className="text-xs font-medium">Contracts</span>
              </div>
              <p className="text-2xl font-bold">{data.contracts.toLocaleString()}</p>
            </div>
            <div className="space-y-1 rounded-lg bg-muted/50 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-xs font-medium">SLA Compliant</span>
              </div>
              <p className="text-2xl font-bold">{slaPercent}%</p>
              <p className="text-xs text-muted-foreground">{data.slaCompliant}/{data.slaTotal}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
