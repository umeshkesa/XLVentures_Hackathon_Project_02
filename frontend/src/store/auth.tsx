import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

export type UserRole = 'admin' | 'customer'

export interface AuthUser {
  email: string
  name: string
  role: UserRole
  customerId?: string
  customerName?: string
}

interface AuthContextValue {
  user: AuthUser | null
  login: (email: string, password: string) => AuthUser | null
  logout: () => void
  isAuthenticated: boolean
  isAdmin: boolean
  isCustomer: boolean
}

const DEMO_ACCOUNTS: Record<string, { password: string; user: AuthUser }> = {
  'admin@adip.ai': {
    password: 'admin123',
    user: { email: 'admin@adip.ai', name: 'Admin', role: 'admin' },
  },
  'novagrid@customer.com': {
    password: 'customer123',
    user: { email: 'novagrid@customer.com', name: 'NovaGrid Energy', role: 'customer', customerId: 'C-1001', customerName: 'NovaGrid Energy' },
  },
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const stored = localStorage.getItem('auth_user')
    if (stored) {
      try { return JSON.parse(stored) as AuthUser } catch { return null }
    }
    return null
  })

  const login = useCallback((email: string, password: string): AuthUser | null => {
    const account = DEMO_ACCOUNTS[email.toLowerCase()]
    if (!account || account.password !== password) return null
    localStorage.setItem('auth_user', JSON.stringify(account.user))
    setUser(account.user)
    return account.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: user !== null,
        isAdmin: user?.role === 'admin',
        isCustomer: user?.role === 'customer',
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
