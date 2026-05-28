import { Link } from 'react-router-dom'
import { ArrowRight, Droplets, Sparkles, Wind, Flower2, Truck, ShieldCheck, RotateCcw, Star } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ProductGrid } from '@/components/catalog/product-grid'
import { useProducts, useCategories } from '@/hooks/use-catalog'
import { storeConfig } from '@/config/store.config'
import { Skeleton } from '@/components/ui/skeleton'

const categoryIcons: Record<string, React.ReactNode> = {
  floral: <Flower2 className="h-6 w-6" />,
  woody: <Wind className="h-6 w-6" />,
  fresh: <Droplets className="h-6 w-6" />,
  oriental: <Sparkles className="h-6 w-6" />,
}

function getCategoryIcon(name: string) {
  const key = name.toLowerCase()
  for (const [k, icon] of Object.entries(categoryIcons)) {
    if (key.includes(k)) return icon
  }
  return <Droplets className="h-6 w-6" />
}

const pressLogos = ['Vogue', 'Harper\'s Bazaar', 'Elle', 'Allure', 'W Magazine']

export function HomePage() {
  const { data, isLoading } = useProducts({ per_page: 8 })
  const { data: categories } = useCategories()

  return (
    <div>
      {/* Hero — single cinematic video */}
      <section className="relative flex min-h-screen items-center overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 h-full w-full object-cover opacity-55 transition-opacity duration-1000"
        >
          <source src="/Deseo_un_video_de_fondo_para_una_tienda_de_perfume_697d86b347.mp4" type="video/mp4" />
        </video>

        {/* Gradient layers for cinematic depth */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-black/60" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/40" />

        <div className="container relative z-10 pb-24 pt-12 text-center">
          {/* Eyebrow */}
          <p className="animate-fade-in text-[11px] font-light uppercase tracking-[0.5em] text-white/50">
            {storeConfig.tagline}
          </p>

          {/* Gold divider */}
          <div className="mx-auto my-6 h-px w-12 bg-gradient-to-r from-transparent via-[hsl(var(--accent))] to-transparent" />

          {/* Main headline */}
          <h1 className="animate-fade-in mx-auto max-w-4xl font-serif text-6xl font-light leading-none tracking-tight text-white md:text-8xl lg:text-9xl">
            Wear Your{' '}
            <em className="block italic text-[hsl(var(--accent))]">Obsession</em>
          </h1>

          <p className="animate-fade-in mx-auto mt-8 max-w-lg text-base font-light leading-relaxed text-white/60">
            Ultra-rare fragrances. Hand-selected from the world's finest perfume houses.
            Created for those who refuse the ordinary.
          </p>

          <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button
              size="lg"
              className="min-w-48 border border-[hsl(var(--accent))] bg-[hsl(var(--accent))] px-10 text-xs uppercase tracking-[0.2em] text-black hover:bg-[hsl(var(--accent))]/90"
              asChild
            >
              <Link to="/products">
                Discover the Collection
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="ghost"
              className="min-w-32 border border-white/20 text-xs uppercase tracking-[0.2em] text-white/80 hover:border-white/40 hover:bg-white/5 hover:text-white"
              asChild
            >
              <Link to="/products">Our Story</Link>
            </Button>
          </div>

          {/* Scroll indicator */}
          <div className="mt-20 flex flex-col items-center gap-2 opacity-40">
            <span className="text-[10px] uppercase tracking-widest text-white">Scroll</span>
            <div className="h-8 w-px animate-pulse bg-white/60" />
          </div>
        </div>
      </section>

      {/* Marquee strip */}
      <section className="overflow-hidden border-y border-[hsl(var(--accent))]/20 bg-black py-4">
        <div className="flex animate-marquee whitespace-nowrap">
          {Array.from({ length: 4 }).map((_, i) => (
            <span key={i} className="mx-0 flex items-center">
              {['Rare Ingredients', 'Small Batch', 'Hand Selected', 'Artisan Crafted', 'Limited Edition', 'Maison Quality', 'Exclusive Access', 'World\'s Finest'].map((text) => (
                <span key={text} className="flex items-center">
                  <span className="px-8 text-[11px] font-light uppercase tracking-[0.3em] text-[hsl(var(--accent))]/70">{text}</span>
                  <span className="text-[hsl(var(--accent))]/30">·</span>
                </span>
              ))}
            </span>
          ))}
        </div>
      </section>

      {/* Editorial — brand statement */}
      <section className="bg-[hsl(var(--primary))] py-24">
        <div className="container max-w-3xl text-center">
          <p className="mb-6 text-[11px] uppercase tracking-[0.4em] text-[hsl(var(--accent))]/60">The Essence Philosophy</p>
          <blockquote className="font-serif text-3xl font-light leading-relaxed text-[hsl(var(--primary-foreground))]/90 md:text-4xl">
            "A great perfume is invisible clothing — it speaks before you say a word,
            and lingers long after you've left the room."
          </blockquote>
          <div className="mx-auto mt-8 h-px w-16 bg-[hsl(var(--accent))]/30" />
          <p className="mt-6 text-sm font-light tracking-widest text-[hsl(var(--primary-foreground))]/40">
            — Founder, ESSENCE Maison
          </p>
        </div>
      </section>

      {/* Press */}
      <section className="border-b bg-[hsl(var(--secondary))]/30 py-12">
        <div className="container">
          <p className="mb-8 text-center text-[10px] uppercase tracking-[0.4em] text-muted-foreground">As Featured In</p>
          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-16">
            {pressLogos.map((name) => (
              <span
                key={name}
                className="font-serif text-lg font-light italic text-muted-foreground/40 transition-colors hover:text-muted-foreground/70"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="border-b bg-background py-16">
        <div className="container">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {([
              { icon: Truck, label: 'Complimentary Shipping', description: 'On orders over $150' },
              { icon: ShieldCheck, label: 'Authenticity Guaranteed', description: '100% genuine fragrances' },
              { icon: Sparkles, label: 'Expert Curation', description: 'Master-selected scents' },
              { icon: RotateCcw, label: 'Effortless Returns', description: '30-day luxury policy' },
            ] as const).map(({ icon: Icon, label, description }) => (
              <div key={label} className="group flex flex-col items-center gap-3 text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[hsl(var(--accent))]/20 bg-[hsl(var(--accent))]/5 transition-colors group-hover:border-[hsl(var(--accent))]/50 group-hover:bg-[hsl(var(--accent))]/10">
                  <Icon className="h-5 w-5 text-[hsl(var(--accent))]" />
                </div>
                <p className="text-sm font-semibold">{label}</p>
                <p className="text-xs text-muted-foreground">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Category showcase */}
      {categories && categories.length > 0 && (
        <section className="py-24">
          <div className="container">
            <div className="mb-12 text-center">
              <p className="mb-3 text-[11px] uppercase tracking-[0.4em] text-[hsl(var(--accent))]/70">Explore</p>
              <h2 className="font-serif text-4xl font-light md:text-5xl">The Collection</h2>
              <div className="mx-auto mt-4 h-px w-16 bg-[hsl(var(--accent))]/30" />
            </div>
            <div className="mx-auto grid max-w-4xl gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {categories.filter(c => c.is_active).map((cat) => (
                <Link
                  key={cat.id}
                  to={`/products?category=${cat.slug}`}
                  className="group relative overflow-hidden rounded-2xl border border-[hsl(var(--accent))]/10 bg-[hsl(var(--primary))] p-8 text-center transition-all hover:border-[hsl(var(--accent))]/40 hover:shadow-[0_8px_32px_rgba(0,0,0,0.3)]"
                >
                  <div className="mb-4 flex h-14 w-14 mx-auto items-center justify-center rounded-full border border-[hsl(var(--accent))]/20 bg-[hsl(var(--accent))]/10 text-[hsl(var(--accent))] transition-colors group-hover:border-[hsl(var(--accent))]/50 group-hover:bg-[hsl(var(--accent))]/20">
                    {getCategoryIcon(cat.name)}
                  </div>
                  <span className="block text-xs font-light uppercase tracking-[0.3em] text-[hsl(var(--primary-foreground))]/80 transition-colors group-hover:text-[hsl(var(--accent))]">
                    {cat.name}
                  </span>
                  <span className="mt-2 block text-[10px] uppercase tracking-widest text-[hsl(var(--primary-foreground))]/30">
                    Shop →
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Scarcity banner */}
      <section className="border-y border-[hsl(var(--accent))]/20 bg-gradient-to-r from-[hsl(var(--primary))] via-[hsl(var(--primary))]/95 to-[hsl(var(--primary))] py-10">
        <div className="container text-center">
          <div className="flex items-center justify-center gap-3 mb-2">
            <div className="h-px flex-1 max-w-16 bg-[hsl(var(--accent))]/30" />
            <span className="text-[10px] uppercase tracking-[0.5em] text-[hsl(var(--accent))]">Limited Availability</span>
            <div className="h-px flex-1 max-w-16 bg-[hsl(var(--accent))]/30" />
          </div>
          <p className="font-serif text-xl font-light text-[hsl(var(--primary-foreground))]/90 md:text-2xl">
            Each fragrance is produced in small, numbered batches.
          </p>
          <p className="mt-2 text-sm text-[hsl(var(--primary-foreground))]/50">
            Once sold out, they may not return. Own yours before someone else does.
          </p>
        </div>
      </section>

      {/* Featured products */}
      <section className="container py-28">
        <div className="mb-14 flex items-end justify-between">
          <div>
            <p className="mb-3 text-[11px] uppercase tracking-[0.4em] text-[hsl(var(--accent))]/70">Curated Selection</p>
            <h2 className="font-serif text-4xl font-light md:text-5xl">Featured Fragrances</h2>
            <div className="mt-4 h-px w-12 bg-[hsl(var(--accent))]/50" />
          </div>
          <Button variant="ghost" className="hidden border border-foreground/10 text-xs uppercase tracking-widest hover:border-[hsl(var(--accent))]/40 sm:inline-flex" asChild>
            <Link to="/products">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
        {isLoading ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="space-y-3">
                <Skeleton className="aspect-square w-full rounded-2xl" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            ))}
          </div>
        ) : data?.items ? (
          <ProductGrid products={data.items} />
        ) : null}
        <div className="mt-10 text-center sm:hidden">
          <Button variant="outline" className="text-xs uppercase tracking-widest" asChild>
            <Link to="/products">
              View All Products
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Testimonials strip */}
      <section className="bg-[hsl(var(--secondary))]/40 py-20">
        <div className="container">
          <div className="mb-10 text-center">
            <p className="text-[11px] uppercase tracking-[0.4em] text-muted-foreground">What Our Clients Say</p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { quote: "The most extraordinary fragrance I have ever worn. Multiple compliments every single day.", author: "S. Laurent", location: "Paris" },
              { quote: "ESSENCE changed how I think about perfume. This isn't just a scent — it's a statement.", author: "M. Ashford", location: "New York" },
              { quote: "Worth every penny. The quality rivals anything I've found in Grasse or Dubai.", author: "A. Yamamoto", location: "Tokyo" },
            ].map(({ quote, author, location }) => (
              <div key={author} className="rounded-2xl border border-[hsl(var(--accent))]/10 bg-background p-8">
                <div className="mb-4 flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-3.5 w-3.5 fill-[hsl(var(--accent))] text-[hsl(var(--accent))]" />
                  ))}
                </div>
                <p className="font-serif text-base font-light italic leading-relaxed text-foreground/80">"{quote}"</p>
                <div className="mt-6 border-t border-[hsl(var(--accent))]/10 pt-4">
                  <p className="text-sm font-semibold">{author}</p>
                  <p className="text-xs text-muted-foreground">{location}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
