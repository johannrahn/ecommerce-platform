import { Link } from 'react-router-dom'
import { Droplets } from 'lucide-react'
import { RatingStars } from './rating-stars'
import { formatCurrency } from '@/lib/utils'
import type { ProductListItem } from '@/types/catalog.types'

interface ProductCardProps {
  product: ProductListItem
}

export function ProductCard({ product }: ProductCardProps) {
  const isVeryLowStock = product.stock > 0 && product.stock <= 3
  const isLowStock = product.stock > 3 && product.stock <= 6

  return (
    <Link to={`/products/${product.slug}`}>
      <div className="group relative overflow-hidden rounded-2xl border border-transparent bg-background transition-all duration-300 hover:border-[hsl(var(--accent))]/30 hover:shadow-[0_12px_40px_rgba(0,0,0,0.12)]">

        {/* Scarcity badge */}
        {isVeryLowStock && (
          <div className="absolute left-3 top-3 z-10 rounded-full border border-red-400/30 bg-black/80 px-2.5 py-1 backdrop-blur-sm">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-red-400">
              Only {product.stock} left
            </span>
          </div>
        )}
        {!isVeryLowStock && isLowStock && (
          <div className="absolute left-3 top-3 z-10 rounded-full border border-[hsl(var(--accent))]/30 bg-black/70 px-2.5 py-1 backdrop-blur-sm">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(var(--accent))]/90">
              Almost Gone
            </span>
          </div>
        )}

        {/* Image */}
        <div className="aspect-square overflow-hidden bg-[hsl(var(--secondary))]">
          {product.primary_image ? (
            <img
              src={product.primary_image}
              alt={product.name}
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-2 bg-gradient-to-br from-[hsl(var(--accent))]/5 to-[hsl(var(--accent))]/15">
              <Droplets className="h-10 w-10 text-[hsl(var(--accent))]/40" />
              <span className="text-xs tracking-widest text-muted-foreground/50">ESSENCE</span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="p-5">
          <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground/60">
            {product.category.name}
          </p>
          <h3 className="mt-1.5 font-serif text-base font-light leading-snug">{product.name}</h3>
          <div className="mt-3 flex items-center justify-between">
            <span className="font-semibold text-foreground">
              {formatCurrency(product.price)}
            </span>
            {product.average_rating && (
              <RatingStars rating={product.average_rating} count={product.reviews_count} />
            )}
          </div>

          {product.stock === 0 ? (
            <p className="mt-2 text-[11px] font-medium uppercase tracking-wider text-destructive">Sold Out</p>
          ) : (
            <div className="mt-3 flex items-center gap-1.5">
              {Array.from({ length: Math.min(product.stock, 10) }).map((_, i) => (
                <div
                  key={i}
                  className={`h-1 flex-1 rounded-full transition-all ${
                    i < product.stock
                      ? product.stock <= 3
                        ? 'bg-red-400/70'
                        : product.stock <= 6
                          ? 'bg-[hsl(var(--accent))]/60'
                          : 'bg-foreground/15'
                      : 'bg-foreground/5'
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}
