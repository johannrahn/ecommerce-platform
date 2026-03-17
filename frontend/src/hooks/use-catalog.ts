import { useQuery } from '@tanstack/react-query'
import * as catalogApi from '@/api/catalog.api'
import { catalogKeys } from '@/lib/query-keys'
import type { ProductQueryParams } from '@/types/catalog.types'

export function useProducts(params: ProductQueryParams = {}) {
  return useQuery({
    queryKey: catalogKeys.products(params),
    queryFn: () => catalogApi.getProducts(params),
    placeholderData: (prev) => prev,
  })
}

export function useProduct(slug: string) {
  return useQuery({
    queryKey: catalogKeys.product(slug),
    queryFn: () => catalogApi.getProductBySlug(slug),
    enabled: !!slug,
  })
}

export function useCategories() {
  return useQuery({
    queryKey: catalogKeys.categories(),
    queryFn: catalogApi.getCategories,
    staleTime: 5 * 60 * 1000,
  })
}
