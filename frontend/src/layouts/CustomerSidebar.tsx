import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  HardDrive,
  MessageSquare,
  BookOpen,
  FileSearch,
  ThumbsUp,
  LifeBuoy,
  User,
  ChevronLeft,
  ChevronRight,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { ScrollArea } from '@radix-ui/react-scroll-area'

const customerNavItems: { label: string; icon: LucideIcon; to: string }[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/customer' },
  { label: 'My Assets', icon: HardDrive, to: '/customer/assets' },
  { label: 'My Interactions', icon: MessageSquare, to: '/customer/interactions' },
  { label: 'Knowledge', icon: BookOpen, to: '/customer/knowledge' },
  { label: 'Evidence', icon: FileSearch, to: '/customer/evidence' },
  { label: 'Recommendations', icon: ThumbsUp, to: '/customer/recommendations' },
  { label: 'Support', icon: LifeBuoy, to: '/customer/support' },
  { label: 'Profile', icon: User, to: '/customer/profile' },
]

interface CustomerSidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function CustomerSidebar({ collapsed, onToggle }: CustomerSidebarProps) {
  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-sidebar-border px-4">
        {!collapsed && (
          <span className="text-lg font-bold tracking-tight">NovaGrid</span>
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
          {customerNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/customer'}
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
