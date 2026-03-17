import { useProductReviews } from '@/hooks/use-reviews'
import { ReviewCard } from './review-card'
import { LoadingSpinner } from '@/components/shared/loading-spinner'

interface ReviewListProps {
  slug: string
}

export function ReviewList({ slug }: ReviewListProps) {
  const { data: reviews, isLoading } = useProductReviews(slug)

  if (isLoading) return <LoadingSpinner />

  if (!reviews?.length) {
    return <p className="text-sm text-muted-foreground">No reviews yet. Be the first!</p>
  }

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <ReviewCard key={review.id} review={review} />
      ))}
    </div>
  )
}
