import apiClient from '@/lib/api-client'
import type { PaginatedOrders, Order, AdminOrderQueryParams } from '@/types/order.types'

export async function adminGetOrders(params: AdminOrderQueryParams = {}): Promise<PaginatedOrders> {
  const { data } = await apiClient.get('/admin/orders', { params })
  return data
}

export async function adminGetOrder(id: string): Promise<Order> {
  const { data } = await apiClient.get(`/admin/orders/${id}`)
  return data
}

export async function adminCancelOrder(id: string): Promise<Order> {
  const { data } = await apiClient.post(`/admin/orders/${id}/cancel`)
  return data
}
