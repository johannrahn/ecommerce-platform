import { Link } from 'react-router-dom'
import { useOrders } from '@/hooks/use-orders'
import { OrderStatusBadge } from '@/components/orders/order-status-badge'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/shared/empty-state'
import { formatCurrency, formatDate } from '@/lib/utils'
import { Package } from 'lucide-react'

const statusBorderColor: Record<string, string> = {
  pending: 'border-l-yellow-400',
  paid: 'border-l-green-400',
  failed: 'border-l-red-400',
  cancelled: 'border-l-gray-400',
}

export function OrdersPage() {
  const { data: orders, isLoading } = useOrders()

  if (isLoading) {
    return (
      <div className="container max-w-3xl py-10">
        <Skeleton className="mb-8 h-9 w-40" />
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-3xl py-10">
      <h1 className="mb-8 font-serif text-3xl font-semibold">My Orders</h1>

      {!orders?.length ? (
        <EmptyState icon={Package} title="No orders yet" description="Start shopping to see your orders here" />
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link key={order.id} to={`/orders/${order.id}`}>
              <div className={`flex items-center justify-between rounded-xl border border-l-4 bg-background p-5 transition-all hover:-translate-y-0.5 hover:shadow-md ${statusBorderColor[order.status] ?? 'border-l-gray-400'}`}>
                <div>
                  <p className="font-medium">Order #{order.id.slice(0, 8)}</p>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    {formatDate(order.created_at)} &middot; {order.items.length} item(s)
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <OrderStatusBadge status={order.status} />
                  <span className="font-bold">{formatCurrency(order.total)}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
