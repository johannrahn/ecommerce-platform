import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { StoreLayout } from '@/components/layout/store-layout'
import { AdminLayout } from '@/components/layout/admin-layout'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { AdminRoute } from '@/components/auth/admin-route'
import { HomePage } from '@/features/store/home-page'
import { ProductsPage } from '@/features/store/products-page'
import { ProductDetailPage } from '@/features/store/product-detail-page'
import { CartPage } from '@/features/store/cart-page'
import { CheckoutPage } from '@/features/store/checkout-page'
import { OrdersPage } from '@/features/store/orders-page'
import { OrderDetailPage } from '@/features/store/order-detail-page'
import { ProfilePage } from '@/features/store/profile-page'
import { LoginPage } from '@/features/store/login-page'
import { RegisterPage } from '@/features/store/register-page'
import { NotFoundPage } from '@/features/store/not-found-page'
import { DashboardPage } from '@/features/admin/dashboard-page'
import { ProductsListPage } from '@/features/admin/products/products-list-page'
import { ProductCreatePage } from '@/features/admin/products/product-create-page'
import { ProductEditPage } from '@/features/admin/products/product-edit-page'
import { CategoriesListPage } from '@/features/admin/categories/categories-list-page'
import { OrdersListPage } from '@/features/admin/orders/orders-list-page'
import { AdminOrderDetailPage } from '@/features/admin/orders/order-detail-page'
import { CouponsListPage } from '@/features/admin/coupons/coupons-list-page'
import { CouponFormPage } from '@/features/admin/coupons/coupon-form-page'
import { ReviewsModerationPage } from '@/features/admin/reviews/reviews-moderation-page'
import { AuditLogsPage } from '@/features/admin/audit/audit-logs-page'

const router = createBrowserRouter([
  {
    element: <StoreLayout />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'products', element: <ProductsPage /> },
      { path: 'products/:slug', element: <ProductDetailPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'cart', element: <CartPage /> },
          { path: 'checkout', element: <CheckoutPage /> },
          { path: 'orders', element: <OrdersPage /> },
          { path: 'orders/:id', element: <OrderDetailPage /> },
          { path: 'profile', element: <ProfilePage /> },
        ],
      },
    ],
  },
  {
    path: 'admin',
    element: <AdminRoute />,
    children: [
      {
        element: <AdminLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: 'products', element: <ProductsListPage /> },
          { path: 'products/new', element: <ProductCreatePage /> },
          { path: 'products/:id/edit', element: <ProductEditPage /> },
          { path: 'categories', element: <CategoriesListPage /> },
          { path: 'orders', element: <OrdersListPage /> },
          { path: 'orders/:id', element: <AdminOrderDetailPage /> },
          { path: 'coupons', element: <CouponsListPage /> },
          { path: 'coupons/new', element: <CouponFormPage /> },
          { path: 'coupons/:id/edit', element: <CouponFormPage /> },
          { path: 'reviews', element: <ReviewsModerationPage /> },
          { path: 'audit-logs', element: <AuditLogsPage /> },
        ],
      },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
