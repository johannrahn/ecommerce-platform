import { ShoppingBag } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUnifiedCart } from '@/hooks/use-unified-cart'
import { useCartUIStore } from '@/stores/cart-ui.store'

export function CartIcon() {
  const { data: cart } = useUnifiedCart()
  const openDrawer = useCartUIStore((s) => s.openDrawer)
  const count = cart?.item_count ?? 0

  return (
    <Button variant="ghost" size="icon" className="relative" onClick={openDrawer}>
      <ShoppingBag className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
          {count}
        </span>
      )}
    </Button>
  )
}
