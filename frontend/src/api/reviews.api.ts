import apiClient from '@/lib/api-client'
import type { Review, ReviewCreate, ReviewUpdate } from '@/types/review.types'

export async function getProductReviews(slug: string): Promise<Review[]> {
  const { data } = await apiClient.get(`/products/${slug}/reviews`)
  return data
}

export async function createReview(slug: string, payload: ReviewCreate): Promise<Review> {
  const { data } = await apiClient.post(`/products/${slug}/reviews`, payload)
  return data
}

export async function updateReview(reviewId: string, payload: ReviewUpdate): Promise<Review> {
  const { data } = await apiClient.put(`/reviews/${reviewId}`, payload)
  return data
}

export async function deleteReview(reviewId: string): Promise<void> {
  await apiClient.delete(`/reviews/${reviewId}`)
}
