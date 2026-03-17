import { Link } from 'react-router-dom'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { CartItemRow } from './cart-item-row'
import { CartSummary } from './cart-summary'
import { useUnifiedCart } from '@/hooks/use-unified-cart'
import { useAuthStore } from '@/stores/auth.store'
import { useCartUIStore } from '@/stores/cart-ui.store'
import { EmptyState } from '@/components/shared/empty-state'
import { ShoppingBag } from 'lucide-react'

export function CartDrawer() {
  const { isDrawerOpen, closeDrawer } = useCartUIStore()
  const { data: cart } = useUnifiedCart()
  const token = useAuthStore((s) => s.token)

  const itemCount = cart?.items.reduce((sum, i) => sum + i.quantity, 0) ?? 0

  return (
    <Sheet open={isDrawerOpen} onOpenChange={closeDrawer}>
      <SheetContent className="flex w-full flex-col sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="font-serif text-xl">
            Shopping Cart{itemCount > 0 && ` (${itemCount})`}
          </SheetTitle>
        </SheetHeader>

        {!cart || cart.items.length === 0 ? (
          <EmptyState icon={ShoppingBag} title="Your cart is empty" description="Browse our products and add items to your cart" />
        ) : (
          <>
            <div className="flex-1 overflow-y-auto">
              <div className="divide-y">
                {cart.items.map((item) => (
                  <CartItemRow key={item.id} item={item} />
                ))}
              </div>
            </div>
            <div className="mt-auto pt-4">
              <CartSummary cart={cart} />
              <Separator className="my-4" />
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" asChild onClick={closeDrawer}>
                  <Link to="/cart">View Cart</Link>
                </Button>
                <Button className="flex-1" asChild onClick={closeDrawer}>
                  <Link to={token ? '/checkout' : '/login'}>
                    {token ? 'Checkout' : 'Sign in to Checkout'}
                  </Link>
                </Button>
              </div>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
