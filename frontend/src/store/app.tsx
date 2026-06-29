import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from 'react'

interface Notification {
  id: string
  title: string
  description?: string
  read: boolean
  timestamp: Date
}

interface AppContextValue {
  notifications: Notification[]
  addNotification: (n: Omit<Notification, 'id' | 'read' | 'timestamp'>) => void
  markRead: (id: string) => void
  clearAll: () => void
  unreadCount: number
}

const AppContext = createContext<AppContextValue | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = (
    n: Omit<Notification, 'id' | 'read' | 'timestamp'>,
  ) => {
    const notif: Notification = {
      ...n,
      id: crypto.randomUUID(),
      read: false,
      timestamp: new Date(),
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const markRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    )
  }

  const clearAll = () => setNotifications([])

  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <AppContext.Provider
      value={{ notifications, addNotification, markRead, clearAll, unreadCount }}
    >
      {children}
    </AppContext.Provider>
  )
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
