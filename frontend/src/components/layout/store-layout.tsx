import { Outlet } from 'react-router-dom'
import { StoreHeader } from './store-header'
import { StoreFooter } from './store-footer'
import { CartDrawer } from '@/components/cart/cart-drawer'

export function StoreLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <StoreHeader />
      <main className="flex-1">
        <Outlet />
      </main>
      <StoreFooter />
      <CartDrawer />
    </div>
  )
}
