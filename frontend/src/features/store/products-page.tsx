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
    <div className="container py-10">
      <h1 className="mb-8 font-serif text-3xl font-semibold">Products</h1>

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
  )
}
