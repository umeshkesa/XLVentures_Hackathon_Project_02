import { Bell, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { useApp } from '@/store/app'
import { Button } from '@/components/Button'
import { Breadcrumbs } from './Breadcrumbs'
import { UserMenu } from './UserMenu'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { cn } from '@/lib/utils'

export function TopNav() {
  const { theme, toggleTheme } = useTheme()
  const { notifications, markRead, unreadCount } = useApp()

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-4 lg:px-6">
      <Breadcrumbs />

      <div className="flex items-center gap-2">
        {/* Notifications */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 w-80 rounded-lg border bg-popover p-2 text-popover-foreground shadow-md"
              sideOffset={8}
              align="end"
            >
              <div className="mb-2 px-2 text-sm font-semibold">Notifications</div>
              {notifications.length === 0 ? (
                <p className="px-2 py-4 text-center text-sm text-muted-foreground">
                  No notifications
                </p>
              ) : (
                notifications.slice(0, 10).map((n) => (
                  <DropdownMenu.Item
                    key={n.id}
                    onClick={() => markRead(n.id)}
                    className={cn(
                      'flex cursor-pointer flex-col rounded-md px-3 py-2 text-sm outline-none transition-colors hover:bg-accent',
                      !n.read && 'bg-accent/50',
                    )}
                  >
                    <span className="font-medium">{n.title}</span>
                    {n.description && (
                      <span className="text-xs text-muted-foreground">{n.description}</span>
                    )}
                  </DropdownMenu.Item>
                ))
              )}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        {/* Theme toggle */}
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'light' ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>

        <UserMenu />
      </div>
    </header>
  )
}
