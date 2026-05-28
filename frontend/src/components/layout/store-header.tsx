import { Link } from 'react-router-dom'
import { Search, User, Menu, LogOut, Package, UserCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { CartIcon } from '@/components/cart/cart-icon'
import { storeConfig } from '@/config/store.config'
import { useAuthStore } from '@/stores/auth.store'
import { useLogout } from '@/hooks/use-auth'
import { useUIStore } from '@/stores/ui.store'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

export function StoreHeader() {
  // Announcement bar cycling messages
  const announcements = [
    'Complimentary worldwide shipping on orders over $150',
    'Small-batch fragrances · Limited stock available',
    'Authenticity guaranteed on every bottle',
  ]
  const user = useAuthStore((s) => s.user)
  const token = useAuthStore((s) => s.token)
  const logout = useLogout()
  const { mobileMenuOpen, setMobileMenu } = useUIStore()
  const [announcementIdx, setAnnouncementIdx] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setAnnouncementIdx(i => (i + 1) % announcements.length), 4000)
    return () => clearInterval(id)
  }, [announcements.length])

  const navLinks = (
    <>
      <Link to="/products" className="text-sm font-medium tracking-wide uppercase transition-colors hover:text-accent">
        Shop
      </Link>
    </>
  )

  return (
    <header className="sticky top-0 z-50">
      {/* Announcement bar */}
      <div className="bg-[hsl(var(--primary))] py-2 text-center">
        <p className="text-[11px] font-light uppercase tracking-[0.25em] text-[hsl(var(--primary-foreground))]/60 transition-all">
          {announcements[announcementIdx]}
        </p>
      </div>

      {/* Main header */}
      <div className="bg-background/95 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between md:h-20">
        {/* Mobile menu */}
        <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenu}>
          <SheetTrigger asChild className="md:hidden">
            <Button variant="ghost" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64">
            <div className="mt-6 mb-8">
              <span className="font-serif text-xl font-semibold tracking-widest">{storeConfig.name}</span>
            </div>
            <nav className="flex flex-col gap-4">{navLinks}</nav>
          </SheetContent>
        </Sheet>

        {/* Logo */}
        <Link to="/" className="font-serif text-2xl font-semibold tracking-widest md:text-3xl">
          {storeConfig.name}
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-8 md:flex">{navLinks}</nav>

        {/* Right actions */}
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/products">
              <Search className="h-5 w-5" />
            </Link>
          </Button>

          <CartIcon />

          {token ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <div className="px-2 py-1.5 text-sm font-medium">
                  {user?.full_name}
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/profile">
                    <UserCircle className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/orders">
                    <Package className="mr-2 h-4 w-4" />
                    Orders
                  </Link>
                </DropdownMenuItem>
                {user?.role === 'admin' && (
                  <DropdownMenuItem asChild>
                    <Link to="/admin">Admin Panel</Link>
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button variant="ghost" size="sm" className="text-sm tracking-wide" asChild>
              <Link to="/login">Sign In</Link>
            </Button>
          )}
        </div>
      </div>
      </div>
    </header>
  )
}
