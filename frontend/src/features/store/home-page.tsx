import { Link } from 'react-router-dom'
import { ArrowRight, Droplets, Sparkles, Wind, Flower2, Truck, ShieldCheck, RotateCcw } from 'lucide-react'
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

export function HomePage() {
  const { data, isLoading } = useProducts({ per_page: 8 })
  const { data: categories } = useCategories()

  return (
    <div>
      {/* Hero */}
      <section className="relative flex min-h-[70vh] items-center bg-gradient-to-br from-primary/95 via-primary/80 to-primary/40">
        <div className="absolute inset-0 overflow-hidden">
          <video autoPlay loop muted playsInline className="absolute top-0 left-0 h-full w-1/2 object-cover">
            <source src="/Deseo_un_video_de_fondo_para_una_tienda_de_perfume_697d86b347.mp4" type="video/mp4" />
          </video>
          <video autoPlay loop muted playsInline className="absolute top-0 right-0 h-full w-1/2 object-cover">
            <source src="/Deseo_un_video_de_fondo_para_una_tienda_de_perfume_04b6afeb76.mp4" type="video/mp4" />
          </video>
          {/* Overlay to ensure text readability */}
          <div className="absolute inset-0 bg-black/40" />
        </div>
        <div className="container relative z-10 py-20 text-center">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-primary-foreground/60">
            {storeConfig.tagline}
          </p>
          <h1 className="mx-auto mt-6 max-w-3xl font-serif text-5xl font-semibold leading-tight tracking-tight text-primary-foreground md:text-7xl">
            Find Your{' '}
            <span className="italic text-accent">Signature</span>{' '}
            Scent
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg text-primary-foreground/70">
            {storeConfig.heroSubtitle}
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Button size="lg" variant="secondary" className="px-8 text-sm uppercase tracking-widest" asChild>
              <Link to="/products">
                Explore Collection
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Brand strip */}
      <section className="border-b bg-background py-16">
        <div className="container text-center">
          <div className="mx-auto flex items-center justify-center gap-4">
            <div className="hidden h-px w-16 bg-accent/40 sm:block" />
            <p className="font-serif text-lg italic text-muted-foreground md:text-xl">
              Crafted with intention. Worn with confidence.
            </p>
            <div className="hidden h-px w-16 bg-accent/40 sm:block" />
          </div>
        </div>
      </section>

      {/* Trust section */}
      <section className="border-b bg-background py-12">
        <div className="container">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            {([
              { icon: Truck, label: 'Free Shipping', description: 'On all orders' },
              { icon: ShieldCheck, label: 'Secure Checkout', description: '100% protected' },
              { icon: Sparkles, label: 'Curated Selection', description: 'Expert-chosen scents' },
              { icon: RotateCcw, label: 'Easy Returns', description: '30-day policy' },
            ] as const).map(({ icon: Icon, label, description }) => (
              <div key={label} className="flex flex-col items-center gap-2 text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10">
                  <Icon className="h-5 w-5 text-accent" />
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
        <section className="bg-secondary/30 py-20">
          <div className="container">
            <div className="mb-10 text-center">
              <h2 className="font-serif text-3xl font-semibold md:text-4xl">Shop by Category</h2>
              <p className="mt-2 text-sm text-muted-foreground">Find the fragrance family that speaks to you</p>
            </div>
            <div className="mx-auto grid max-w-4xl gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {categories.filter(c => c.is_active).map((cat) => (
                <Link
                  key={cat.id}
                  to={`/products?category=${cat.slug}`}
                  className="group flex flex-col items-center gap-3 rounded-xl bg-background p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10 text-accent transition-colors group-hover:bg-accent/20">
                    {getCategoryIcon(cat.name)}
                  </div>
                  <span className="text-sm font-medium uppercase tracking-widest">{cat.name}</span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Featured products */}
      <section className="container py-24">
        <div className="mb-12 flex items-center justify-between">
          <div>
            <h2 className="font-serif text-3xl font-semibold md:text-4xl">Featured Products</h2>
            <div className="mt-2 h-0.5 w-12 bg-accent" />
          </div>
          <Button variant="outline" className="hidden sm:inline-flex" asChild>
            <Link to="/products">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="space-y-3">
                <Skeleton className="aspect-square w-full rounded-xl" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            ))}
          </div>
        ) : data?.items ? (
          <ProductGrid products={data.items} />
        ) : null}
        <div className="mt-8 text-center sm:hidden">
          <Button variant="outline" asChild>
            <Link to="/products">
              View All Products
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
