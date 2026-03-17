import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from '@/components/ui/sonner'
import { queryClient } from '@/lib/query-client'
import { useAuthStore } from '@/stores/auth.store'
import { getMe } from '@/api/users.api'
import App from './App'
import '@/styles/globals.css'

async function bootstrap() {
  const token = useAuthStore.getState().token
  if (token) {
    try {
      const user = await getMe()
      useAuthStore.getState().setUser(user)
    } catch {
      useAuthStore.getState().logout()
    }
  }

  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster position="bottom-right" />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </StrictMode>,
  )
}

bootstrap()
