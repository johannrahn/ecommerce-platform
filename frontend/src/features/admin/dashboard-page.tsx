import { ShoppingCart, Package, Users, DollarSign } from 'lucide-react'
import { StatCard } from '@/components/shared/stat-card'
import { useAdminOrders } from '@/hooks/use-admin-orders'
import { useAdminProducts } from '@/hooks/use-admin-catalog'
import { formatCurrency } from '@/lib/utils'

export function DashboardPage() {
  const { data: ordersData } = useAdminOrders({ limit: 1000 })
  const { data: productsData } = useAdminProducts({ per_page: 1 })

  const orders = ordersData?.items ?? []
  const totalRevenue = orders
    .filter((o) => o.status === 'paid')
    .reduce((sum, o) => sum + o.total, 0)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Orders" value={ordersData?.total ?? 0} icon={ShoppingCart} />
        <StatCard label="Revenue" value={formatCurrency(totalRevenue)} icon={DollarSign} />
        <StatCard label="Products" value={productsData?.total ?? 0} icon={Package} />
        <StatCard
          label="Paid Orders"
          value={orders.filter((o) => o.status === 'paid').length}
          icon={Users}
        />
      </div>
    </div>
  )
}
