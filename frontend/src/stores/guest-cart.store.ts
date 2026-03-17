import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface GuestCartItem {
  product_id: string
  product_slug: string
  product_name: string
  product_price: number
  primary_image: string | null
  quantity: number
}

interface GuestCartState {
  items: GuestCartItem[]
  addItem: (item: GuestCartItem) => void
  updateItem: (product_id: string, quantity: number) => void
  removeItem: (product_id: string) => void
  clearItems: () => void
}

export const useGuestCartStore = create<GuestCartState>()(
  persist(
    (set) => ({
      items: [],

      addItem: (incoming) =>
        set((state) => {
          const existing = state.items.find((i) => i.product_id === incoming.product_id)
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.product_id === incoming.product_id
                  ? { ...i, quantity: i.quantity + incoming.quantity }
                  : i
              ),
            }
          }
          return { items: [...state.items, incoming] }
        }),

      updateItem: (product_id, quantity) =>
        set((state) => ({
          items:
            quantity <= 0
              ? state.items.filter((i) => i.product_id !== product_id)
              : state.items.map((i) =>
                  i.product_id === product_id ? { ...i, quantity } : i
                ),
        })),

      removeItem: (product_id) =>
        set((state) => ({
          items: state.items.filter((i) => i.product_id !== product_id),
        })),

      clearItems: () => set({ items: [] }),
    }),
    { name: 'guest-cart' }
  )
)
