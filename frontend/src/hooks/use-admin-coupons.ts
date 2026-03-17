import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as promotionsApi from '@/api/promotions-admin.api'
import { adminCouponKeys } from '@/lib/query-keys'
import { toast } from 'sonner'
import type { CouponCreate, CouponUpdate } from '@/types/promotion.types'

export function useAdminCoupons() {
  return useQuery({
    queryKey: adminCouponKeys.all(),
    queryFn: promotionsApi.adminGetCoupons,
  })
}

export function useAdminCoupon(id: string) {
  return useQuery({
    queryKey: adminCouponKeys.detail(id),
    queryFn: () => promotionsApi.adminGetCoupon(id),
    enabled: !!id,
  })
}

export function useCreateCoupon() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CouponCreate) => promotionsApi.adminCreateCoupon(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'coupons'] })
      toast.success('Coupon created')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useUpdateCoupon() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CouponUpdate }) =>
      promotionsApi.adminUpdateCoupon(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'coupons'] })
      toast.success('Coupon updated')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
