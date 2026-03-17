import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as reviewsApi from '@/api/reviews.api'
import { reviewKeys } from '@/lib/query-keys'
import { toast } from 'sonner'
import type { ReviewCreate, ReviewUpdate } from '@/types/review.types'

export function useProductReviews(slug: string) {
  return useQuery({
    queryKey: reviewKeys.byProduct(slug),
    queryFn: () => reviewsApi.getProductReviews(slug),
    enabled: !!slug,
  })
}

export function useCreateReview(slug: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: ReviewCreate) => reviewsApi.createReview(slug, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.byProduct(slug) })
      toast.success('Review submitted!')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useUpdateReview(slug: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ reviewId, payload }: { reviewId: string; payload: ReviewUpdate }) =>
      reviewsApi.updateReview(reviewId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.byProduct(slug) })
      toast.success('Review updated')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useDeleteReview(slug: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reviewId: string) => reviewsApi.deleteReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.byProduct(slug) })
      toast.success('Review deleted')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
