import { useParams } from 'react-router-dom'
import { useOrder } from '@/hooks/use-orders'
import { OrderStatusBadge } from '@/components/orders/order-status-badge'
import { OrderItemsTable } from '@/components/orders/order-items-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { formatCurrency, formatDateTime } from '@/lib/utils'

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: order, isLoading } = useOrder(id!)

  if (isLoading) {
    return (
      <div className="container max-w-3xl py-10">
        <Skeleton className="mb-8 h-9 w-64" />
        <Skeleton className="h-80 w-full rounded-xl" />
      </div>
    )
  }

  if (!order) return <div className="container py-8">Order not found</div>

  return (
    <div className="container max-w-3xl py-10">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-serif text-2xl font-semibold">Order #{order.id.slice(0, 8)}</h1>
        <OrderStatusBadge status={order.status} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Items</CardTitle>
        </CardHeader>
        <CardContent>
          <OrderItemsTable items={order.items} />

          <Separator className="my-6" />

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Subtotal</span>
              <span>{formatCurrency(order.subtotal)}</span>
            </div>
            {order.discount_amount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount {order.coupon_code && `(${order.coupon_code})`}</span>
                <span>-{formatCurrency(order.discount_amount)}</span>
              </div>
            )}
            <div className="flex justify-between border-t pt-3 text-lg font-bold">
              <span>Total</span>
              <span>{formatCurrency(order.total)}</span>
            </div>
          </div>

          <Separator className="my-6" />

          <p className="text-sm text-muted-foreground">
            Placed on {formatDateTime(order.created_at)}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
