import { useState } from 'react'
import { useProducts } from '@/hooks/use-catalog'
import { useProductReviews } from '@/hooks/use-reviews'
import { useAdminHideReview, useAdminUnhideReview } from '@/hooks/use-admin-reviews'
import { PageHeader } from '@/components/shared/page-header'
import { RatingStars } from '@/components/catalog/rating-stars'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { LoadingSpinner } from '@/components/shared/loading-spinner'
import { Eye, EyeOff } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

export function ReviewsModerationPage() {
  const [selectedSlug, setSelectedSlug] = useState<string>('')
  const { data: productsData } = useProducts({ per_page: 100 })
  const { data: reviews, isLoading } = useProductReviews(selectedSlug)
  const hideReview = useAdminHideReview()
  const unhideReview = useAdminUnhideReview()

  return (
    <div className="space-y-6">
      <PageHeader title="Reviews Moderation" description="Moderate product reviews" />

      <Select value={selectedSlug} onValueChange={setSelectedSlug}>
        <SelectTrigger className="w-64">
          <SelectValue placeholder="Select a product" />
        </SelectTrigger>
        <SelectContent>
          {productsData?.items.map((p) => (
            <SelectItem key={p.slug} value={p.slug}>{p.name}</SelectItem>
          ))}
        </SelectContent>
      </Select>

      {!selectedSlug ? (
        <p className="text-muted-foreground">Select a product to view its reviews.</p>
      ) : isLoading ? (
        <LoadingSpinner />
      ) : !reviews?.length ? (
        <p className="text-muted-foreground">No reviews for this product.</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead>Comment</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Visible</TableHead>
                <TableHead className="w-16" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {reviews.map((review) => (
                <TableRow key={review.id}>
                  <TableCell>{review.user_name}</TableCell>
                  <TableCell><RatingStars rating={review.rating} /></TableCell>
                  <TableCell className="max-w-xs truncate">{review.comment ?? '-'}</TableCell>
                  <TableCell className="text-sm">{formatRelativeTime(review.created_at)}</TableCell>
                  <TableCell>
                    <Badge variant={review.is_visible ? 'default' : 'secondary'}>
                      {review.is_visible ? 'Visible' : 'Hidden'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {review.is_visible ? (
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => hideReview.mutate(review.id)}>
                        <EyeOff className="h-4 w-4" />
                      </Button>
                    ) : (
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => unhideReview.mutate(review.id)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
