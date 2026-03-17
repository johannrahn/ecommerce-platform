import apiClient from '@/lib/api-client'
import type { PaginatedProducts, Product, Category, ProductQueryParams } from '@/types/catalog.types'

export async function getProducts(params: ProductQueryParams = {}): Promise<PaginatedProducts> {
  const { data } = await apiClient.get('/catalog/products', { params })
  return data
}

export async function getProductBySlug(slug: string): Promise<Product> {
  const { data } = await apiClient.get(`/catalog/products/${slug}`)
  return data
}

export async function getCategories(): Promise<Category[]> {
  const { data } = await apiClient.get('/catalog/categories')
  return data
}

export async function getCategoryBySlug(slug: string): Promise<Category> {
  const { data } = await apiClient.get(`/catalog/categories/${slug}`)
  return data
}
