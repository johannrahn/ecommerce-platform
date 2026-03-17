import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as adminOrdersApi from '@/api/orders-admin.api'
import { adminOrderKeys } from '@/lib/query-keys'
import { toast } from 'sonner'
import type { AdminOrderQueryParams } from '@/types/order.types'

export function useAdminOrders(params: AdminOrderQueryParams = {}) {
  return useQuery({
    queryKey: adminOrderKeys.list(params),
    queryFn: () => adminOrdersApi.adminGetOrders(params),
    placeholderData: (prev) => prev,
  })
}

export function useAdminOrder(id: string) {
  return useQuery({
    queryKey: adminOrderKeys.detail(id),
    queryFn: () => adminOrdersApi.adminGetOrder(id),
    enabled: !!id,
  })
}

export function useCancelOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => adminOrdersApi.adminCancelOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'orders'] })
      toast.success('Order cancelled')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
