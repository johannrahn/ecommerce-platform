import { Link } from 'react-router-dom'
import { useUnifiedCart } from '@/hooks/use-unified-cart'
import { useClearCart } from '@/hooks/use-cart'
import { useAuthStore } from '@/stores/auth.store'
import { useGuestCartStore } from '@/stores/guest-cart.store'
import { CartItemRow } from '@/components/cart/cart-item-row'
import { CartSummary } from '@/components/cart/cart-summary'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/shared/empty-state'
import { Skeleton } from '@/components/ui/skeleton'
import { ShoppingBag, Trash2 } from 'lucide-react'

export function CartPage() {
  const { data: cart, isLoading } = useUnifiedCart()
  const clearCart = useClearCart()
  const token = useAuthStore((s) => s.token)
  const clearGuestCart = useGuestCartStore((s) => s.clearItems)

  if (isLoading) {
    return (
      <div className="container max-w-3xl py-10">
        <Skeleton className="mb-6 h-9 w-48" />
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-3xl py-10">
      <h1 className="mb-8 font-serif text-3xl font-semibold">Shopping Cart</h1>

      {!cart || cart.items.length === 0 ? (
        <EmptyState
          icon={ShoppingBag}
          title="Your cart is empty"
          description="Browse our products and add items to your cart"
          action={{ label: 'Shop Now', onClick: () => window.location.href = '/products' }}
        />
      ) : (
        <div className="space-y-6">
          <div className="flex justify-end">
            <Button
              variant="outline"
              size="sm"
              onClick={() => token ? clearCart.mutate() : clearGuestCart()}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Clear Cart
            </Button>
          </div>

          <div className="divide-y rounded-xl border p-4">
            {cart.items.map((item) => (
              <CartItemRow key={item.id} item={item} />
            ))}
          </div>

          <CartSummary cart={cart} />

          <Button size="lg" className="w-full" asChild>
            <Link to={token ? '/checkout' : '/login'}>
              {token ? 'Proceed to Checkout' : 'Sign in to Checkout'}
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}
