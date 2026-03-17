import apiClient from '@/lib/api-client'
import type { Notification } from '@/types/notification.types'

export async function getNotifications(): Promise<Notification[]> {
  const { data } = await apiClient.get('/notifications')
  return data
}

export async function markAsRead(notificationId: string): Promise<Notification> {
  const { data } = await apiClient.post(`/notifications/${notificationId}/read`)
  return data
}

export async function markAllAsRead(): Promise<{ marked_read: number }> {
  const { data } = await apiClient.post('/notifications/read-all')
  return data
}
