import { Link } from 'react-router-dom'
import { Droplets } from 'lucide-react'
import { RatingStars } from './rating-stars'
import { formatCurrency } from '@/lib/utils'
import type { ProductListItem } from '@/types/catalog.types'

interface ProductCardProps {
  product: ProductListItem
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link to={`/products/${product.slug}`}>
      <div className="group overflow-hidden rounded-xl bg-background transition-all hover:-translate-y-1 hover:shadow-lg">
        <div className="aspect-square overflow-hidden bg-secondary">
          {product.primary_image ? (
            <img
              src={product.primary_image}
              alt={product.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-2 bg-gradient-to-br from-accent/5 to-accent/15">
              <Droplets className="h-10 w-10 text-accent/40" />
              <span className="text-xs text-muted-foreground/50">ESSENCE</span>
            </div>
          )}
        </div>
        <div className="p-4">
          <p className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground/70">
            {product.category.name}
          </p>
          <h3 className="mt-1.5 font-semibold leading-tight">{product.name}</h3>
          <div className="mt-3 flex items-center justify-between">
            <span className="text-lg font-bold text-accent-foreground">
              {formatCurrency(product.price)}
            </span>
            {product.average_rating && (
              <RatingStars rating={product.average_rating} count={product.reviews_count} />
            )}
          </div>
          {product.stock === 0 && (
            <p className="mt-1.5 text-xs font-medium text-destructive">Out of stock</p>
          )}
        </div>
      </div>
    </Link>
  )
}
