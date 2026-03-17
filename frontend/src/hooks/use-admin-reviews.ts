import { useMutation, useQueryClient } from '@tanstack/react-query'
import * as adminReviewsApi from '@/api/reviews-admin.api'
import { toast } from 'sonner'

export function useAdminHideReview() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reviewId: string) => adminReviewsApi.adminHideReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
      toast.success('Review hidden')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useAdminUnhideReview() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reviewId: string) => adminReviewsApi.adminUnhideReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
      toast.success('Review unhidden')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
