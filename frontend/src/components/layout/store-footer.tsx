import { Link } from 'react-router-dom'
import { storeConfig } from '@/config/store.config'

export function StoreFooter() {
  return (
    <footer className="bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
      {/* Gold divider */}
      <div className="h-px w-full bg-gradient-to-r from-transparent via-[hsl(var(--accent))]/40 to-transparent" />

      <div className="container py-20">
        <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="lg:col-span-1">
            <h3 className="font-serif text-3xl font-light tracking-[0.3em]">{storeConfig.name}</h3>
            <div className="my-4 h-px w-8 bg-[hsl(var(--accent))]/40" />
            <p className="text-sm font-light leading-relaxed text-[hsl(var(--primary-foreground))]/50">
              {storeConfig.description}
            </p>
            <p className="mt-3 text-[11px] uppercase tracking-[0.3em] text-[hsl(var(--accent))]/60">
              {storeConfig.tagline}
            </p>
          </div>

          {/* Shop */}
          <div>
            <h4 className="mb-5 text-[10px] font-semibold uppercase tracking-[0.4em] text-[hsl(var(--primary-foreground))]/30">
              Shop
            </h4>
            <nav className="flex flex-col gap-3">
              {['All Fragrances', 'Eau de Parfum', 'Eau de Toilette', 'Gift Sets', 'New Arrivals'].map((item) => (
                <Link
                  key={item}
                  to="/products"
                  className="text-sm font-light text-[hsl(var(--primary-foreground))]/50 transition-colors hover:text-[hsl(var(--accent))]"
                >
                  {item}
                </Link>
              ))}
            </nav>
          </div>

          {/* Contact */}
          <div>
            <h4 className="mb-5 text-[10px] font-semibold uppercase tracking-[0.4em] text-[hsl(var(--primary-foreground))]/30">
              Client Services
            </h4>
            <div className="flex flex-col gap-3">
              <p className="text-sm font-light text-[hsl(var(--primary-foreground))]/50">
                {storeConfig.contact.email}
              </p>
              <p className="text-sm font-light text-[hsl(var(--primary-foreground))]/50">
                {storeConfig.contact.phone}
              </p>
              <p className="mt-2 text-[11px] leading-relaxed text-[hsl(var(--primary-foreground))]/30">
                Mon – Fri, 9AM – 6PM EST<br />
                Concierge available 24/7
              </p>
            </div>
          </div>

          {/* Social & promise */}
          <div>
            <h4 className="mb-5 text-[10px] font-semibold uppercase tracking-[0.4em] text-[hsl(var(--primary-foreground))]/30">
              Our Promise
            </h4>
            <div className="flex flex-col gap-3">
              {['100% Authentic', 'Small Batch Only', 'Free Returns', 'Discreet Packaging'].map((item) => (
                <p key={item} className="flex items-center gap-2 text-sm font-light text-[hsl(var(--primary-foreground))]/50">
                  <span className="text-[hsl(var(--accent))]/60">—</span>
                  {item}
                </p>
              ))}
            </div>
            <div className="mt-8 flex gap-4">
              <a
                href={storeConfig.social.instagram}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] uppercase tracking-[0.3em] text-[hsl(var(--primary-foreground))]/30 transition-colors hover:text-[hsl(var(--accent))]"
              >
                Instagram
              </a>
              <a
                href={storeConfig.social.twitter}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] uppercase tracking-[0.3em] text-[hsl(var(--primary-foreground))]/30 transition-colors hover:text-[hsl(var(--accent))]"
              >
                Twitter
              </a>
            </div>
          </div>
        </div>

        <div className="mt-16 border-t border-[hsl(var(--primary-foreground))]/5 pt-8 flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between">
          <p className="text-[11px] text-[hsl(var(--primary-foreground))]/25">
            {storeConfig.footerText}
          </p>
          <p className="text-[11px] text-[hsl(var(--primary-foreground))]/20">
            Crafted with intention. Worn with confidence.
          </p>
        </div>
      </div>
    </footer>
  )
}
