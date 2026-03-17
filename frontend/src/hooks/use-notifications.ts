import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as notificationsApi from '@/api/notifications.api'
import { notificationKeys } from '@/lib/query-keys'
import { useAuthStore } from '@/stores/auth.store'

export function useNotifications() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: notificationKeys.mine(),
    queryFn: notificationsApi.getNotifications,
    enabled: !!token,
    refetchInterval: 60 * 1000,
  })
}

export function useMarkAsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all })
    },
  })
}

export function useMarkAllAsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all })
    },
  })
}
