import { useState } from 'react'
import { Droplets } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ProductImage } from '@/types/catalog.types'

interface ProductImagesProps {
  images: ProductImage[]
  productName: string
}

export function ProductImages({ images, productName }: ProductImagesProps) {
  const sorted = [...images].sort((a, b) => a.sort_order - b.sort_order)
  const [selected, setSelected] = useState(0)

  if (sorted.length === 0) {
    return (
      <div className="flex aspect-square flex-col items-center justify-center gap-3 rounded-xl bg-gradient-to-br from-accent/5 to-accent/15 shadow-sm">
        <Droplets className="h-16 w-16 text-accent/30" />
        <span className="text-sm text-muted-foreground/50">No image available</span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="aspect-square overflow-hidden rounded-xl bg-secondary shadow-sm">
        <img
          src={sorted[selected].url}
          alt={productName}
          className="h-full w-full object-cover"
        />
      </div>
      {sorted.length > 1 && (
        <div className="flex gap-3">
          {sorted.map((img, i) => (
            <button
              key={img.id}
              onClick={() => setSelected(i)}
              className={cn(
                'h-20 w-20 overflow-hidden rounded-lg border-2 transition-all',
                selected === i ? 'border-accent shadow-sm' : 'border-transparent opacity-60 hover:opacity-100'
              )}
            >
              <img src={img.url} alt="" className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
