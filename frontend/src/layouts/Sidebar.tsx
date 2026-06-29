import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Users,
  HardDrive,
  Upload,
  MessageSquare,
  BookOpen,
  FileSearch,
  BrainCircuit,
  ThumbsUp,
  ClipboardCheck,
  GitMerge,
  Zap,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ClipboardList,
  Activity,
  Puzzle,
  HeartPulse,
  TrendingUp,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { ScrollArea } from '@radix-ui/react-scroll-area'

interface NavItem {
  label: string
  icon: LucideIcon
  to: string
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/dashboard' },
  { label: 'Customers', icon: Users, to: '/customers' },
  { label: 'Assets', icon: HardDrive, to: '/assets' },
  { label: 'Import Center', icon: Upload, to: '/import' },
  { label: 'Interactions', icon: MessageSquare, to: '/interactions' },
  { label: 'Knowledge', icon: BookOpen, to: '/knowledge' },
  { label: 'Evidence', icon: FileSearch, to: '/evidence' },
  { label: 'Reasoning', icon: BrainCircuit, to: '/reasoning' },
  { label: 'Planner', icon: ClipboardList, to: '/planner' },
  { label: 'Recommendations', icon: ThumbsUp, to: '/recommendations' },
  { label: 'Explainability', icon: GitMerge, to: '/explainability' },
  { label: 'Decision Review', icon: ClipboardCheck, to: '/review' },
  { label: 'Actions', icon: Zap, to: '/actions' },
  { label: 'AI Copilot', icon: Sparkles, to: '/copilot' },
  { label: 'Agents', icon: Activity, to: '/agents' },
  { label: 'Plugins', icon: Puzzle, to: '/plugins' },
  { label: 'Health', icon: HeartPulse, to: '/health' },
  { label: 'Analytics', icon: TrendingUp, to: '/analytics' },
  { label: 'Settings', icon: Settings, to: '/settings' },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-sidebar-border px-4">
        {!collapsed && (
          <span className="text-lg font-bold tracking-tight">ADIP</span>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="ml-auto text-sidebar-foreground"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>
      <ScrollArea className="flex-1 overflow-y-auto">
        <nav className="flex flex-col gap-1 p-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                  collapsed && 'justify-center px-2',
                )
              }
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </ScrollArea>
    </aside>
  )
}
