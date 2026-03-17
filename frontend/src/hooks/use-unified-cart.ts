import { toast } from 'sonner'
import { useAuthStore } from '@/stores/auth.store'
import { useGuestCartStore, type GuestCartItem } from '@/stores/guest-cart.store'
import {
  useCart,
  useAddToCart,
  useUpdateCartItem,
  useRemoveCartItem,
} from '@/hooks/use-cart'
import type { Cart, CartItem, CartItemAdd, CartItemUpdate } from '@/types/cart.types'

// ─── Guest → Cart shape conversion ───────────────────────────────────────────

function guestItemsToCart(items: GuestCartItem[]): Cart {
  const cartItems: CartItem[] = items.map((g) => ({
    id: g.product_id, // item.id === product_id for guest items
    product_id: g.product_id,
    product_name: g.product_name,
    product_price: g.product_price,
    product_slug: g.product_slug,
    primary_image: g.primary_image,
    quantity: g.quantity,
    subtotal: g.product_price * g.quantity,
    created_at: new Date().toISOString(),
  }))
  return {
    id: 'guest',
    items: cartItems,
    item_count: cartItems.reduce((s, i) => s + i.quantity, 0),
    total: cartItems.reduce((s, i) => s + i.subtotal, 0),
    coupon_code: null,
    updated_at: new Date().toISOString(),
  }
}

// ─── Extended payload type for unified add ───────────────────────────────────

export interface UnifiedAddPayload extends CartItemAdd {
  product_name?: string
  product_price?: number
  product_slug?: string
  primary_image?: string | null
}

// ─── Hooks ───────────────────────────────────────────────────────────────────

export function useUnifiedCart() {
  const token = useAuthStore((s) => s.token)
  const guestItems = useGuestCartStore((s) => s.items)
  const backendCart = useCart() // always called — hook rules

  if (token) {
    return { ...backendCart, isGuest: false }
  }

  return {
    data: guestItems.length > 0 ? guestItemsToCart(guestItems) : null,
    isLoading: false,
    isPending: false,
    isError: false,
    error: null,
    isGuest: true,
  }
}

export function useUnifiedAddToCart() {
  const token = useAuthStore((s) => s.token)
  const guestStore = useGuestCartStore()
  const backendAdd = useAddToCart() // always called — hook rules

  if (token) return backendAdd

  return {
    mutate: (payload: UnifiedAddPayload) => {
      guestStore.addItem({
        product_id: payload.product_id,
        product_slug: payload.product_slug ?? '',
        product_name: payload.product_name ?? '',
        product_price: payload.product_price ?? 0,
        primary_image: payload.primary_image ?? null,
        quantity: payload.quantity,
      })
      toast.success('Added to cart')
    },
    isPending: false,
    isError: false,
    error: null,
  }
}

export function useUnifiedUpdateCartItem() {
  const token = useAuthStore((s) => s.token)
  const guestStore = useGuestCartStore()
  const backendUpdate = useUpdateCartItem() // always called — hook rules

  if (token) return backendUpdate

  return {
    mutate: ({ itemId, payload }: { itemId: string; payload: CartItemUpdate }) => {
      guestStore.updateItem(itemId, payload.quantity)
    },
    isPending: false,
    isError: false,
    error: null,
  }
}

export function useUnifiedRemoveCartItem() {
  const token = useAuthStore((s) => s.token)
  const guestStore = useGuestCartStore()
  const backendRemove = useRemoveCartItem() // always called — hook rules

  if (token) return backendRemove

  return {
    mutate: (itemId: string) => {
      guestStore.removeItem(itemId)
      toast.success('Item removed')
    },
    isPending: false,
    isError: false,
    error: null,
  }
}
