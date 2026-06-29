import { RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/hooks/useTheme'
import { AppProvider } from '@/store/app'
import { Toaster } from 'sonner'
import { router } from '@/routes'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppProvider>
          <RouterProvider router={router} />
          <Toaster richColors closeButton position="top-right" />
        </AppProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
