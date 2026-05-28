import { useState } from 'react'
import { useProducts, useCategories } from '@/hooks/use-catalog'
import { useDebounce } from '@/hooks/use-debounce'
import { ProductGrid } from '@/components/catalog/product-grid'
import { SearchBar } from '@/components/catalog/search-bar'
import { CategoryFilter } from '@/components/catalog/category-filter'
import { PaginationControls } from '@/components/catalog/pagination-controls'
import { ProductGridSkeleton } from '@/components/shared/skeleton-cards'
import { EmptyState } from '@/components/shared/empty-state'
import { Search } from 'lucide-react'
import { DEFAULT_PAGE_SIZE } from '@/lib/constants'

export function ProductsPage() {
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState<string | undefined>()
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebounce(search, 300)

  const { data: categories } = useCategories()
  const { data, isLoading } = useProducts({
    search: debouncedSearch || undefined,
    category_id: categoryId,
    page,
    per_page: DEFAULT_PAGE_SIZE,
  })

  return (
    <div>
      {/* Cinematic header with video and fade-out */}
      <div className="relative h-[38vh] min-h-[220px] overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 h-full w-full object-cover opacity-45"
        >
          <source src="/Deseo_un_video_de_fondo_para_una_tienda_de_perfume_04b6afeb76.mp4" type="video/mp4" />
        </video>

        {/* Fading overlays — creates smooth transition into the page below */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-background" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/30 via-transparent to-black/30" />

        {/* Header text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase tracking-[0.5em] text-white/40">ESSENCE Maison</p>
          <h1 className="mt-3 font-serif text-4xl font-light tracking-wide text-white md:text-6xl">
            The Collection
          </h1>
          <div className="mx-auto mt-4 h-px w-10 bg-[hsl(var(--accent))]/60" />
          <p className="mt-3 text-sm font-light text-white/50">
            {data?.total ? `${data.total} exclusive fragrances` : 'Discover rare fragrances'}
          </p>
        </div>
      </div>

      {/* Filters and grid */}
      <div className="container py-10">
        <div className="mb-8 space-y-4">
          <SearchBar value={search} onChange={(v) => { setSearch(v); setPage(1) }} />
          {categories && (
            <CategoryFilter
              categories={categories.filter((c) => c.is_active)}
              selected={categoryId}
              onSelect={(id) => { setCategoryId(id); setPage(1) }}
            />
          )}
        </div>

        {isLoading ? (
          <ProductGridSkeleton count={DEFAULT_PAGE_SIZE} />
        ) : data?.items.length ? (
          <>
            <ProductGrid products={data.items} />
            <div className="mt-10">
              <PaginationControls page={data.page} pages={data.pages} onPageChange={setPage} />
            </div>
          </>
        ) : (
          <EmptyState icon={Search} title="No products found" description="Try adjusting your search or filters" />
        )}
      </div>
    </div>
  )
}
