import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import * as Avatar from '@radix-ui/react-avatar'
import { LogOut, User, Settings } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function UserMenu() {
  const navigate = useNavigate()

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center gap-2 rounded-md p-1.5 text-sm transition-colors hover:bg-accent outline-none">
          <Avatar.Root className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
            <Avatar.Fallback>AD</Avatar.Fallback>
          </Avatar.Root>
          <span className="hidden md:inline font-medium">Admin</span>
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="z-50 min-w-44 rounded-lg border bg-popover p-1 text-popover-foreground shadow-md"
          sideOffset={8}
          align="end"
        >
          <DropdownMenu.Item
            onClick={() => navigate('/settings')}
            className="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm outline-none transition-colors hover:bg-accent"
          >
            <User className="h-4 w-4" />
            Profile
          </DropdownMenu.Item>
          <DropdownMenu.Item
            onClick={() => navigate('/settings')}
            className="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm outline-none transition-colors hover:bg-accent"
          >
            <Settings className="h-4 w-4" />
            Settings
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="mx-1 my-1 h-px bg-border" />
          <DropdownMenu.Item className="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm outline-none transition-colors hover:bg-accent text-destructive">
            <LogOut className="h-4 w-4" />
            Sign out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
