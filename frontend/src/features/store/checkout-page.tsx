import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '@/hooks/use-cart'
import { useUnifiedCart } from '@/hooks/use-unified-cart'
import { useCheckout } from '@/hooks/use-orders'
import { useAuthStore } from '@/stores/auth.store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/shared/empty-state'
import { formatCurrency } from '@/lib/utils'
import { Loader2, ShoppingBag, ShoppingCart, CreditCard, Check } from 'lucide-react'

const steps = [
  { label: 'Cart', icon: ShoppingCart },
  { label: 'Checkout', icon: CreditCard },
  { label: 'Done', icon: Check },
]

export function CheckoutPage() {
  const token = useAuthStore((s) => s.token)
  const { data: unifiedCart } = useUnifiedCart()
  const { data: cart, isLoading: cartLoading } = useCart()
  const checkout = useCheckout()
  const navigate = useNavigate()

  const handleCheckout = () => {
    checkout.mutate(undefined, {
      onSuccess: (response) => {
        if (response.order.status === 'paid') {
          navigate(`/orders/${response.order.id}`)
        }
      },
    })
  }

  // Guest auth gate — show cart summary + sign-in prompt
  if (!token) {
    return (
      <div className="container max-w-2xl py-10">
        <h1 className="mb-6 font-serif text-3xl font-semibold">Checkout</h1>

        {unifiedCart && unifiedCart.items.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Your Cart</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {unifiedCart.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {item.product_name} <span className="text-foreground font-medium">×{item.quantity}</span>
                  </span>
                  <span className="font-medium">{formatCurrency(item.subtotal)}</span>
                </div>
              ))}
              <Separator />
              <div className="flex items-center justify-between font-bold">
                <span>Total</span>
                <span>{formatCurrency(unifiedCart.total)}</span>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardContent className="py-10 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 mx-auto mb-4">
              <ShoppingBag className="h-7 w-7 text-accent" />
            </div>
            <h2 className="font-serif text-xl font-semibold">Sign in to complete your order</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Your cart will be saved. Create an account or sign in to place your order.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <Button asChild>
                <Link to="/login">Sign In</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/register">Create Account</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (cartLoading) {
    return (
      <div className="container max-w-2xl py-10">
        <Skeleton className="mb-10 h-8 w-48" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container py-8">
        <EmptyState icon={ShoppingBag} title="Nothing to checkout" description="Add items to your cart first" />
      </div>
    )
  }

  return (
    <div className="container max-w-2xl py-10">
      {/* Step indicator */}
      <div className="mb-10 flex items-center justify-center gap-2">
        {steps.map((step, i) => (
          <div key={step.label} className="flex items-center gap-2">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${
              i <= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
            }`}>
              <step.icon className="h-4 w-4" />
            </div>
            <span className={`text-sm ${i <= 1 ? 'font-medium' : 'text-muted-foreground'}`}>
              {step.label}
            </span>
            {i < steps.length - 1 && <div className="mx-2 h-px w-8 bg-border" />}
          </div>
        ))}
      </div>

      <h1 className="mb-6 font-serif text-3xl font-semibold">Checkout</h1>

      <Card>
        <CardHeader>
          <CardTitle>Order Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {cart.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span>
                {item.product_name} x {item.quantity}
              </span>
              <span>{formatCurrency(item.subtotal)}</span>
            </div>
          ))}

          <Separator />

          {cart.coupon_code && (
            <div className="flex justify-between text-sm text-green-600">
              <span>Coupon: {cart.coupon_code}</span>
              <span>Applied</span>
            </div>
          )}

          <div className="flex justify-between border-t pt-3 text-lg font-bold">
            <span>Total</span>
            <span>{formatCurrency(cart.total)}</span>
          </div>

          <Button
            size="lg"
            className="w-full"
            onClick={handleCheckout}
            disabled={checkout.isPending}
          >
            {checkout.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Place Order
          </Button>

          <p className="text-center text-xs text-muted-foreground">
            This is a simulated payment. No real charges will be made.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
