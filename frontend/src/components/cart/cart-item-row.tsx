import { Minus, Plus, Trash2, Droplets } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUnifiedUpdateCartItem, useUnifiedRemoveCartItem } from '@/hooks/use-unified-cart'
import { formatCurrency } from '@/lib/utils'
import type { CartItem } from '@/types/cart.types'
import { Link } from 'react-router-dom'

interface CartItemRowProps {
  item: CartItem
}

export function CartItemRow({ item }: CartItemRowProps) {
  const updateItem = useUnifiedUpdateCartItem()
  const removeItem = useUnifiedRemoveCartItem()

  return (
    <div className="flex gap-4 py-4">
      <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg bg-secondary">
        {item.primary_image ? (
          <img src={item.primary_image} alt={item.product_name} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-1 bg-gradient-to-br from-accent/5 to-accent/15">
            <Droplets className="h-6 w-6 text-accent/30" />
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col justify-between">
        <div>
          <Link to={`/products/${item.product_slug}`} className="font-medium hover:underline">
            {item.product_name}
          </Link>
          <p className="text-sm text-muted-foreground">{formatCurrency(item.product_price)}</p>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="h-7 w-7 rounded-full"
              onClick={() =>
                updateItem.mutate({
                  itemId: item.id,
                  payload: { quantity: Math.max(1, item.quantity - 1) },
                })
              }
              disabled={item.quantity <= 1}
            >
              <Minus className="h-3 w-3" />
            </Button>
            <span className="w-6 text-center text-sm font-medium">{item.quantity}</span>
            <Button
              variant="outline"
              size="icon"
              className="h-7 w-7 rounded-full"
              onClick={() =>
                updateItem.mutate({
                  itemId: item.id,
                  payload: { quantity: item.quantity + 1 },
                })
              }
            >
              <Plus className="h-3 w-3" />
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <span className="font-semibold">{formatCurrency(item.subtotal)}</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-destructive hover:text-destructive"
              onClick={() => removeItem.mutate(item.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
