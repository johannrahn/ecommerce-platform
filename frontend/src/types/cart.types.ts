export interface CartItem {
  id: string
  product_id: string
  product_name: string
  product_price: number
  product_slug: string
  primary_image: string | null
  quantity: number
  subtotal: number
  created_at: string
}

export interface Cart {
  id: string
  items: CartItem[]
  item_count: number
  total: number
  coupon_code: string | null
  updated_at: string
}

export interface CartItemAdd {
  product_id: string
  quantity: number
}

export interface CartItemUpdate {
  quantity: number
}

export interface ApplyCoupon {
  code: string
}
