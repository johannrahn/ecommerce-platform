import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as cartApi from '@/api/cart.api'
import { cartKeys } from '@/lib/query-keys'
import { useAuthStore } from '@/stores/auth.store'
import { toast } from 'sonner'
import type { CartItemAdd, CartItemUpdate } from '@/types/cart.types'

export function useCart() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: cartKeys.mine(),
    queryFn: cartApi.getCart,
    enabled: !!token,
  })
}

export function useAddToCart() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CartItemAdd) => cartApi.addItem(payload),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
      toast.success('Added to cart')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ itemId, payload }: { itemId: string; payload: CartItemUpdate }) =>
      cartApi.updateItem(itemId, payload),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) => cartApi.removeItem(itemId),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
      toast.success('Item removed')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useApplyCoupon() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (code: string) => cartApi.applyCoupon({ code }),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
      toast.success('Coupon applied!')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useRemoveCoupon() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => cartApi.removeCoupon(),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
      toast.success('Coupon removed')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useClearCart() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => cartApi.clearCart(),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(cartKeys.mine(), updatedCart)
      toast.success('Cart cleared')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
