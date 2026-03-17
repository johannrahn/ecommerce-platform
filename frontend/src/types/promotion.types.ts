export type DiscountType = 'percent' | 'fixed'

export interface Coupon {
  id: string
  code: string
  description: string | null
  discount_type: DiscountType
  discount_value: number
  minimum_order_amount: number | null
  max_discount_amount: number | null
  max_uses: number | null
  used_count: number
  is_active: boolean
  starts_at: string | null
  ends_at: string | null
  one_per_user: boolean
  created_at: string
  updated_at: string
}

export interface CouponCreate {
  code: string
  description?: string
  discount_type: DiscountType
  discount_value: number
  minimum_order_amount?: number
  max_discount_amount?: number
  max_uses?: number
  is_active?: boolean
  starts_at?: string
  ends_at?: string
  one_per_user?: boolean
}

export interface CouponUpdate {
  code?: string
  description?: string
  discount_type?: DiscountType
  discount_value?: number
  minimum_order_amount?: number | null
  max_discount_amount?: number | null
  max_uses?: number | null
  is_active?: boolean
  starts_at?: string | null
  ends_at?: string | null
  one_per_user?: boolean
}
