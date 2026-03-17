import apiClient from '@/lib/api-client'
import type { Coupon, CouponCreate, CouponUpdate } from '@/types/promotion.types'

export async function adminGetCoupons(): Promise<Coupon[]> {
  const { data } = await apiClient.get('/admin/coupons')
  return data
}

export async function adminGetCoupon(id: string): Promise<Coupon> {
  const { data } = await apiClient.get(`/admin/coupons/${id}`)
  return data
}

export async function adminCreateCoupon(payload: CouponCreate): Promise<Coupon> {
  const { data } = await apiClient.post('/admin/coupons', payload)
  return data
}

export async function adminUpdateCoupon(id: string, payload: CouponUpdate): Promise<Coupon> {
  const { data } = await apiClient.put(`/admin/coupons/${id}`, payload)
  return data
}
