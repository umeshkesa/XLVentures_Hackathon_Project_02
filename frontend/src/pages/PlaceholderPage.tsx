import { EmptyState } from '@/components/EmptyState'

interface PlaceholderPageProps {
  title: string
  description?: string
}

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {description && (
          <p className="text-muted-foreground">{description}</p>
        )}
      </div>
      <EmptyState
        title={title}
        description="This module is coming soon. Business logic will be implemented in subsequent phases."
      />
    </div>
  )
}
