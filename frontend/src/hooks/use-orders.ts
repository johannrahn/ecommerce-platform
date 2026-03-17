import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as ordersApi from '@/api/orders.api'
import { orderKeys, cartKeys } from '@/lib/query-keys'
import { useAuthStore } from '@/stores/auth.store'
import { toast } from 'sonner'

export function useOrders() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: orderKeys.list(),
    queryFn: ordersApi.getOrders,
    enabled: !!token,
  })
}

export function useOrder(id: string) {
  return useQuery({
    queryKey: orderKeys.detail(id),
    queryFn: () => ordersApi.getOrderById(id),
    enabled: !!id,
  })
}

export function useCheckout() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ordersApi.checkout,
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all })
      queryClient.invalidateQueries({ queryKey: orderKeys.all })
      if (response.order.status === 'paid') {
        toast.success('Order placed successfully!')
      } else {
        toast.error(response.payment_message)
      }
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
