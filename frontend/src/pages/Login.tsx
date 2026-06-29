import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/store/auth'
import { Button } from '@/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/Card'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = login(email, password)
      if (user) {
        navigate(user.role === 'admin' ? '/dashboard' : '/customer', { replace: true })
      } else {
        setError('Invalid email or password')
      }
    } catch {
      setError('An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (email: string, password: string) => {
    setEmail(email)
    setPassword(password)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary text-xl font-bold text-primary-foreground">
            A
          </div>
          <CardTitle className="text-2xl">Welcome to ADIP</CardTitle>
          <CardDescription>
            Sign in to the Agentic Decision Intelligence Platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter your password"
                required
              />
            </div>
            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" loading={loading}>
              Sign in
            </Button>
          </form>

          <div className="mt-6 space-y-3 border-t pt-4">
            <p className="text-xs text-muted-foreground text-center">
              Demo Accounts
            </p>
            <button
              type="button"
              onClick={() => fillDemo('admin@adip.ai', 'admin123')}
              className="w-full rounded-md border bg-card p-3 text-left text-sm transition-colors hover:bg-accent"
            >
              <span className="font-medium">Admin</span>
              <span className="ml-2 text-muted-foreground">admin@adip.ai</span>
            </button>
            <button
              type="button"
              onClick={() => fillDemo('novagrid@customer.com', 'customer123')}
              className="w-full rounded-md border bg-card p-3 text-left text-sm transition-colors hover:bg-accent"
            >
              <span className="font-medium">Customer</span>
              <span className="ml-2 text-muted-foreground">novagrid@customer.com</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
