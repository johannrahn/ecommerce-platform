import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useApplyCoupon, useRemoveCoupon } from '@/hooks/use-cart'
import { formatCurrency } from '@/lib/utils'
import { X, Tag } from 'lucide-react'
import type { Cart } from '@/types/cart.types'

interface CartSummaryProps {
  cart: Cart
}

export function CartSummary({ cart }: CartSummaryProps) {
  const [couponCode, setCouponCode] = useState('')
  const applyCoupon = useApplyCoupon()
  const removeCoupon = useRemoveCoupon()

  const subtotal = cart.items.reduce((sum, i) => sum + i.subtotal, 0)

  return (
    <div className="space-y-4">
      {cart.coupon_code ? (
        <div className="flex items-center justify-between rounded-md border-l-4 border-accent bg-accent/5 px-3 py-2 text-sm">
          <div className="flex items-center gap-2">
            <Tag className="h-4 w-4 text-accent" />
            <span className="font-medium">{cart.coupon_code}</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => removeCoupon.mutate()}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (couponCode.trim()) {
              applyCoupon.mutate(couponCode.trim())
              setCouponCode('')
            }
          }}
          className="flex gap-2"
        >
          <Input
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value)}
            placeholder="Coupon code"
            className="flex-1"
          />
          <Button type="submit" variant="outline" disabled={applyCoupon.isPending}>
            Apply
          </Button>
        </form>
      )}

      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Subtotal</span>
          <span>{formatCurrency(subtotal)}</span>
        </div>
        <div className="flex items-center justify-between border-t pt-3 text-lg font-bold">
          <span>Total</span>
          <span>{formatCurrency(cart.total)}</span>
        </div>
      </div>
    </div>
  )
}
