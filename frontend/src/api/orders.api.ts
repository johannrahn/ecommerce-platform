import apiClient from '@/lib/api-client'
import type { CheckoutResponse, Order } from '@/types/order.types'
import { v4 as uuidv4 } from 'uuid'

export async function checkout(): Promise<CheckoutResponse> {
  const idempotencyKey = uuidv4()
  const { data } = await apiClient.post('/orders/checkout', null, {
    headers: { 'Idempotency-Key': idempotencyKey },
  })
  return data
}

export async function getOrders(): Promise<Order[]> {
  const { data } = await apiClient.get('/orders')
  return data
}

export async function getOrderById(id: string): Promise<Order> {
  const { data } = await apiClient.get(`/orders/${id}`)
  return data
}
