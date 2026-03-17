export type OrderStatus = 'pending' | 'paid' | 'failed' | 'cancelled'

export interface OrderItem {
  id: string
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  subtotal: number
}

export interface Order {
  id: string
  status: OrderStatus
  subtotal: number
  discount_amount: number
  total: number
  coupon_code: string | null
  items: OrderItem[]
  created_at: string
  updated_at: string
}

export interface PaginatedOrders {
  items: Order[]
  total: number
  limit: number
  offset: number
}

export interface CheckoutResponse {
  order: Order
  payment_message: string
}

export interface AdminOrderQueryParams {
  limit?: number
  offset?: number
  status?: OrderStatus
  user_id?: string
}
