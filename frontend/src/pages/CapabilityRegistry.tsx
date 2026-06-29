import { useState, useMemo } from 'react'
import { DEFAULT_PLUGINS, DEFAULT_CAPABILITIES, DOMAIN_PLUGIN_COLORS } from '@/types/plugins'
import type { PluginItem, PluginCapability } from '@/types/plugins'
import { cn } from '@/lib/utils'
import {
  Puzzle, Search, Filter, CheckCircle2, AlertTriangle, Clock,
  Box, Code, Package,
} from 'lucide-react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Button } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'

type TabType = 'plugins' | 'capabilities'
type DomainFilter = string | 'all'
type StatusFilter = 'all' | 'active' | 'inactive' | 'error'

export default function CapabilityRegistry() {
  const [activeTab, setActiveTab] = useState<TabType>('plugins')
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState<DomainFilter>('all')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null)

  const plugins = DEFAULT_PLUGINS as PluginItem[]
  const capabilities = DEFAULT_CAPABILITIES as PluginCapability[]

  const domains = useMemo(() => {
    const d = new Set(plugins.map(p => p.domain))
    return Array.from(d).sort()
  }, [plugins])

  const filteredPlugins = useMemo(() => {
    return plugins.filter(p => {
      if (domainFilter !== 'all' && p.domain !== domainFilter) return false
      if (statusFilter !== 'all' && p.status !== statusFilter) return false
      if (search && !p.name.toLowerCase().includes(search.toLowerCase()) && !p.description.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [plugins, search, domainFilter, statusFilter])

  const filteredCapabilities = useMemo(() => {
    return capabilities.filter(c => {
      if (domainFilter !== 'all' && c.domain !== domainFilter) return false
      if (search && !c.name.toLowerCase().includes(search.toLowerCase()) && !c.description.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [capabilities, search, domainFilter])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Plugin & Capability Registry</h1>
        <p className="text-sm text-muted-foreground mt-1">Browse registered plugins, tools, and available capabilities</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{plugins.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Plugins</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{plugins.filter(p => p.status === 'active').length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Active</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{capabilities.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Capabilities</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{domains.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Domains</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{plugins.reduce((s, p) => s + p.capabilities.length, 0)}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Tools</div>
        </Card>
      </div>

      <div className="flex gap-1 border-b">
        {(['plugins', 'capabilities'] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={cn('px-4 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize', activeTab === tab ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground')}>
            {tab === 'plugins' ? 'Registered Plugins' : 'Available Capabilities'}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-background border rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" />
        </div>
        <Filter className="h-4 w-4 text-muted-foreground" />
        <select value={domainFilter} onChange={e => setDomainFilter(e.target.value as DomainFilter)}
          className="bg-background border rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
          <option value="all">All Domains</option>
          {domains.map(d => <option key={d} value={d} className="capitalize">{d}</option>)}
        </select>
        {activeTab === 'plugins' && (
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as StatusFilter)}
            className="bg-background border rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="error">Error</option>
          </select>
        )}
      </div>

      {activeTab === 'plugins' && (
        <div className="grid gap-4">
          {filteredPlugins.length === 0 ? (
            <EmptyState title="No Plugins Found" description="No plugins match your search criteria." icon={<Puzzle className="h-12 w-12" />} />
          ) : (
            filteredPlugins.map(p => (
              <Card key={p.id} className={cn('p-4 transition-all', selectedPlugin === p.id && 'ring-2 ring-primary/30')}>
                <div className="flex items-start gap-4">
                  <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border', DOMAIN_PLUGIN_COLORS[p.domain] ?? 'text-slate-500 bg-slate-500/10')}>
                    <Package className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-sm font-semibold">{p.name}</h3>
                      <Badge variant="outline" className="text-[10px]">v{p.version}</Badge>
                      <Badge className={cn('text-[10px]', p.status === 'active' ? 'bg-green-500/10 text-green-600 border-green-500/30' : p.status === 'inactive' ? 'bg-slate-500/10 text-slate-600' : 'bg-red-500/10 text-red-600')}>
                        {p.status === 'active' ? <CheckCircle2 className="h-3 w-3 mr-0.5" /> : p.status === 'inactive' ? <Clock className="h-3 w-3 mr-0.5" /> : <AlertTriangle className="h-3 w-3 mr-0.5" />}
                        {p.status}
                      </Badge>
                      <Badge variant="outline" className="text-[10px]">{p.domain}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{p.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-[10px] text-muted-foreground">
                      <span>By {p.author}</span>
                      <span>{p.health}% health</span>
                      <span>{p.capabilities.length} capabilities</span>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {p.capabilities.map(c => (
                        <Badge key={c} variant="outline" className="text-[9px]">{c}</Badge>
                      ))}
                    </div>
                    {p.dependencies.length > 0 && (
                      <div className="flex items-center gap-1 mt-2 text-[10px] text-muted-foreground">
                        <span>Dependencies:</span>
                        {p.dependencies.map(d => (
                          <Badge key={d} variant="outline" className="text-[9px]">{d}</Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button variant="outline" size="sm" className="shrink-0 text-xs" onClick={() => setSelectedPlugin(selectedPlugin === p.id ? null : p.id)}>
                    {selectedPlugin === p.id ? 'Close' : 'Details'}
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'capabilities' && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filteredCapabilities.length === 0 ? (
            <div className="col-span-full">
              <EmptyState title="No Capabilities Found" description="No capabilities match your search criteria." icon={<Code className="h-12 w-12" />} />
            </div>
          ) : (
            filteredCapabilities.map(c => (
              <Card key={`${c.plugin_id}-${c.name}`} className="p-4">
                <div className="flex items-start gap-3">
                  <div className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border', DOMAIN_PLUGIN_COLORS[c.domain] ?? 'text-slate-500 bg-slate-500/10')}>
                    <Box className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="text-sm font-semibold">{c.name}</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">{c.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-[10px]">{c.domain}</Badge>
                      <Badge variant="outline" className="text-[10px]">{c.plugin_id}</Badge>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  )
}
