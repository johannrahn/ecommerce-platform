import { useParams } from 'react-router-dom'
import { useAdminOrder, useCancelOrder } from '@/hooks/use-admin-orders'
import { OrderStatusBadge } from '@/components/orders/order-status-badge'
import { OrderItemsTable } from '@/components/orders/order-items-table'
import { PageHeader } from '@/components/shared/page-header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { LoadingSpinner } from '@/components/shared/loading-spinner'
import { formatCurrency, formatDateTime } from '@/lib/utils'

export function AdminOrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: order, isLoading } = useAdminOrder(id!)
  const cancelOrder = useCancelOrder()

  if (isLoading) return <LoadingSpinner fullScreen />
  if (!order) return <div>Order not found</div>

  return (
    <div className="space-y-6">
      <PageHeader title={`Order #${order.id.slice(0, 8)}`}>
        <OrderStatusBadge status={order.status} />
        {(order.status === 'pending' || order.status === 'paid') && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => cancelOrder.mutate(order.id)}
            disabled={cancelOrder.isPending}
          >
            Cancel Order
          </Button>
        )}
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Items</CardTitle>
        </CardHeader>
        <CardContent>
          <OrderItemsTable items={order.items} />
          <Separator className="my-4" />
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{formatCurrency(order.subtotal)}</span>
            </div>
            {order.discount_amount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount {order.coupon_code && `(${order.coupon_code})`}</span>
                <span>-{formatCurrency(order.discount_amount)}</span>
              </div>
            )}
            <div className="flex justify-between text-lg font-bold">
              <span>Total</span>
              <span>{formatCurrency(order.total)}</span>
            </div>
          </div>
          <Separator className="my-4" />
          <p className="text-sm text-muted-foreground">
            Created: {formatDateTime(order.created_at)} | Updated: {formatDateTime(order.updated_at)}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
