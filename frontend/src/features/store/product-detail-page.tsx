import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useProduct, useProducts } from '@/hooks/use-catalog'
import { useUnifiedAddToCart } from '@/hooks/use-unified-cart'
import { ProductImages } from '@/components/catalog/product-images'
import { ProductCard } from '@/components/catalog/product-card'
import { RatingStars } from '@/components/catalog/rating-stars'
import { ReviewList } from '@/components/reviews/review-list'
import { ReviewForm } from '@/components/reviews/review-form'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/stores/auth.store'
import { formatCurrency } from '@/lib/utils'
import { ShoppingBag, ChevronRight, Minus, Plus } from 'lucide-react'

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const { data: product, isLoading } = useProduct(slug!)
  const addToCart = useUnifiedAddToCart()
  const token = useAuthStore((s) => s.token)
  const [quantity, setQuantity] = useState(1)

  // Related products — same category, fetched after product loads
  const { data: relatedData } = useProducts({
    category_id: product?.category_id,
    per_page: 8,
  })
  const relatedProducts = relatedData?.items
    .filter((p) => p.id !== product?.id)
    .slice(0, 4) ?? []

  if (isLoading) {
    return (
      <div className="container py-10">
        <Skeleton className="mb-8 h-4 w-48" />
        <div className="grid gap-10 md:grid-cols-2">
          <Skeleton className="aspect-square w-full rounded-xl" />
          <div className="space-y-4">
            <Skeleton className="h-5 w-24" />
            <Skeleton className="h-9 w-3/4" />
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-12 w-48" />
          </div>
        </div>
      </div>
    )
  }

  if (!product) return <div className="container py-8">Product not found</div>

  const maxQty = product.stock
  const primaryImage =
    product.images.find((i) => i.is_primary)?.url ??
    product.images[0]?.url ??
    null

  return (
    <div className="container py-10">
      {/* Breadcrumb */}
      <nav className="mb-8 flex items-center gap-1.5 text-sm text-muted-foreground">
        <Link to="/" className="transition-colors hover:text-foreground">Home</Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <Link to="/products" className="transition-colors hover:text-foreground">Products</Link>
        <ChevronRight className="h-3.5 w-3.5" />
        <span className="text-foreground">{product.name}</span>
      </nav>

      <div className="grid gap-10 md:grid-cols-2">
        <ProductImages images={product.images} productName={product.name} />

        <div className="space-y-5">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground/70">
              {product.category.name}
            </p>
            <h1 className="mt-2 font-serif text-3xl font-semibold md:text-4xl">{product.name}</h1>
          </div>

          {product.average_rating && (
            <RatingStars rating={product.average_rating} count={product.reviews_count} size="md" />
          )}

          <p className="text-3xl font-bold text-accent-foreground">
            {formatCurrency(product.price)}
          </p>

          {/* About this Fragrance */}
          {product.description && (
            <div className="rounded-lg border-l-4 border-accent bg-accent/5 p-4">
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-widest text-accent">
                About this Fragrance
              </h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{product.description}</p>
            </div>
          )}

          {/* Stock indicator */}
          <div className="flex items-center gap-2 text-sm">
            <span className={`inline-block h-2 w-2 rounded-full ${product.stock > 0 ? 'bg-green-500' : 'bg-destructive'}`} />
            {product.stock > 0 ? (
              <span className="text-green-600">{product.stock} in stock</span>
            ) : (
              <span className="text-destructive">Out of stock</span>
            )}
          </div>

          {/* Quantity selector */}
          {product.stock > 0 && (
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Quantity</span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8 rounded-full"
                  onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                  disabled={quantity <= 1}
                >
                  <Minus className="h-3 w-3" />
                </Button>
                <span className="w-8 text-center font-medium">{quantity}</span>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8 rounded-full"
                  onClick={() => setQuantity((q) => Math.min(maxQty, q + 1))}
                  disabled={quantity >= maxQty}
                >
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
            </div>
          )}

          {/* CTA */}
          <Button
            size="lg"
            className="w-full md:w-auto"
            disabled={product.stock === 0 || addToCart.isPending}
            onClick={() =>
              addToCart.mutate({
                product_id: product.id,
                quantity,
                product_name: product.name,
                product_price: product.price,
                product_slug: product.slug,
                primary_image: primaryImage,
              })
            }
          >
            <ShoppingBag className="mr-2 h-5 w-5" />
            Add to Cart
          </Button>
        </div>
      </div>

      {/* Reviews */}
      <Separator className="my-16" />
      <div className="space-y-6">
        <div>
          <h2 className="font-serif text-2xl font-semibold">
            Reviews{product.reviews_count ? ` (${product.reviews_count})` : ''}
          </h2>
          <div className="mt-2 h-0.5 w-10 bg-accent" />
        </div>
        {token && <ReviewForm slug={slug!} />}
        <ReviewList slug={slug!} />
      </div>

      {/* You may also like */}
      {relatedProducts.length > 0 && (
        <>
          <Separator className="my-16" />
          <section>
            <h2 className="font-serif text-2xl font-semibold">You may also like</h2>
            <div className="mt-2 mb-8 h-0.5 w-10 bg-accent" />
            <div className="grid gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
              {relatedProducts.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}
