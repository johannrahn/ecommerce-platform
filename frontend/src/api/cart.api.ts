import apiClient from '@/lib/api-client'
import type { Cart, CartItemAdd, CartItemUpdate, ApplyCoupon } from '@/types/cart.types'

export async function getCart(): Promise<Cart> {
  const { data } = await apiClient.get('/cart')
  return data
}

export async function addItem(payload: CartItemAdd): Promise<Cart> {
  const { data } = await apiClient.post('/cart/items', payload)
  return data
}

export async function updateItem(itemId: string, payload: CartItemUpdate): Promise<Cart> {
  const { data } = await apiClient.put(`/cart/items/${itemId}`, payload)
  return data
}

export async function removeItem(itemId: string): Promise<Cart> {
  const { data } = await apiClient.delete(`/cart/items/${itemId}`)
  return data
}

export async function applyCoupon(payload: ApplyCoupon): Promise<Cart> {
  const { data } = await apiClient.post('/cart/coupon', payload)
  return data
}

export async function removeCoupon(): Promise<Cart> {
  const { data } = await apiClient.delete('/cart/coupon')
  return data
}

export async function clearCart(): Promise<Cart> {
  const { data } = await apiClient.delete('/cart')
  return data
}
