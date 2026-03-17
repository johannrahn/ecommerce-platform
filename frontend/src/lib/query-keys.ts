import type { ProductQueryParams, AdminProductQueryParams } from '@/types/catalog.types'
import type { AdminOrderQueryParams } from '@/types/order.types'
import type { AuditQueryParams } from '@/types/audit.types'

export const catalogKeys = {
  all: ['catalog'] as const,
  products: (params: ProductQueryParams) => ['catalog', 'products', params] as const,
  product: (slug: string) => ['catalog', 'product', slug] as const,
  categories: () => ['catalog', 'categories'] as const,
  category: (slug: string) => ['catalog', 'category', slug] as const,
}

export const cartKeys = {
  all: ['cart'] as const,
  mine: () => ['cart', 'mine'] as const,
}

export const orderKeys = {
  all: ['orders'] as const,
  list: () => ['orders', 'list'] as const,
  detail: (id: string) => ['orders', 'detail', id] as const,
}

export const reviewKeys = {
  byProduct: (slug: string) => ['reviews', 'product', slug] as const,
}

export const notificationKeys = {
  all: ['notifications'] as const,
  mine: () => ['notifications', 'mine'] as const,
}

export const adminCatalogKeys = {
  products: (params: AdminProductQueryParams) => ['admin', 'catalog', 'products', params] as const,
  product: (id: string) => ['admin', 'catalog', 'product', id] as const,
  categories: () => ['admin', 'catalog', 'categories'] as const,
}

export const adminOrderKeys = {
  list: (params: AdminOrderQueryParams) => ['admin', 'orders', params] as const,
  detail: (id: string) => ['admin', 'orders', id] as const,
}

export const adminCouponKeys = {
  all: () => ['admin', 'coupons'] as const,
  detail: (id: string) => ['admin', 'coupons', id] as const,
}

export const adminAuditKeys = {
  list: (params: AuditQueryParams) => ['admin', 'audit', params] as const,
}
