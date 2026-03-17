import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from '@/lib/constants'
import type { OrderStatus } from '@/types/order.types'

interface OrderStatusBadgeProps {
  status: OrderStatus
}

export function OrderStatusBadge({ status }: OrderStatusBadgeProps) {
  return (
    <Badge variant="outline" className={cn('border-none', ORDER_STATUS_COLORS[status])}>
      {ORDER_STATUS_LABELS[status]}
    </Badge>
  )
}
