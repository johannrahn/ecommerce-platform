import { Link } from 'react-router-dom'
import { storeConfig } from '@/config/store.config'

export function StoreFooter() {
  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="container py-16">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <h3 className="font-serif text-2xl font-semibold tracking-widest">{storeConfig.name}</h3>
            <p className="mt-3 text-sm text-primary-foreground/70">{storeConfig.tagline}</p>
            <p className="mt-1 text-sm text-primary-foreground/70">{storeConfig.description}</p>
          </div>

          {/* Shop */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-primary-foreground/50">Shop</h4>
            <nav className="mt-4 flex flex-col gap-2">
              <Link to="/products" className="text-sm text-primary-foreground/70 transition-colors hover:text-primary-foreground">
                All Products
              </Link>
              <Link to="/products" className="text-sm text-primary-foreground/70 transition-colors hover:text-primary-foreground">
                New Arrivals
              </Link>
            </nav>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-primary-foreground/50">Contact</h4>
            <div className="mt-4 flex flex-col gap-2">
              <p className="text-sm text-primary-foreground/70">{storeConfig.contact.email}</p>
              <p className="text-sm text-primary-foreground/70">{storeConfig.contact.phone}</p>
            </div>
          </div>

          {/* Social */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-primary-foreground/50">Follow Us</h4>
            <div className="mt-4 flex flex-col gap-2">
              <a href={storeConfig.social.instagram} target="_blank" rel="noopener noreferrer" className="text-sm text-primary-foreground/70 transition-colors hover:text-primary-foreground">
                Instagram
              </a>
              <a href={storeConfig.social.twitter} target="_blank" rel="noopener noreferrer" className="text-sm text-primary-foreground/70 transition-colors hover:text-primary-foreground">
                Twitter
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 border-t border-primary-foreground/10 pt-6 text-center text-xs text-primary-foreground/40">
          {storeConfig.footerText}
        </div>
      </div>
    </footer>
  )
}
