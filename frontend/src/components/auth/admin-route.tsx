import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth.store'
import { LoadingSpinner } from '@/components/shared/loading-spinner'

export function AdminRoute() {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)

  if (!token) {
    return <Navigate to="/login?redirect=/admin" replace />
  }

  if (user && user.role !== 'admin') {
    return <Navigate to="/" replace />
  }

  if (!user) {
    return <LoadingSpinner fullScreen />
  }

  return <Outlet />
}
