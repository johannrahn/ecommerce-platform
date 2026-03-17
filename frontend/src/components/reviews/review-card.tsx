import { RatingStars } from '@/components/catalog/rating-stars'
import { formatRelativeTime } from '@/lib/utils'
import type { Review } from '@/types/review.types'

interface ReviewCardProps {
  review: Review
}

export function ReviewCard({ review }: ReviewCardProps) {
  return (
    <div className="space-y-2 rounded-lg border p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium">{review.user_name}</p>
          <RatingStars rating={review.rating} />
        </div>
        <span className="text-xs text-muted-foreground">
          {formatRelativeTime(review.created_at)}
        </span>
      </div>
      {review.title && <p className="font-medium">{review.title}</p>}
      {review.comment && <p className="text-sm text-muted-foreground">{review.comment}</p>}
    </div>
  )
}
