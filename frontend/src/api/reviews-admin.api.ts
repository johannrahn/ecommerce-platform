import apiClient from '@/lib/api-client'
import type { Review } from '@/types/review.types'

export async function adminHideReview(reviewId: string): Promise<Review> {
  const { data } = await apiClient.post(`/admin/reviews/${reviewId}/hide`)
  return data
}

export async function adminUnhideReview(reviewId: string): Promise<Review> {
  const { data } = await apiClient.post(`/admin/reviews/${reviewId}/unhide`)
  return data
}
