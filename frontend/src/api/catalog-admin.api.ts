import apiClient from '@/lib/api-client'
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  Category,
  CategoryCreate,
  CategoryUpdate,
  PaginatedProducts,
  AdminProductQueryParams,
  ProductImage,
  ProductImageCreate,
} from '@/types/catalog.types'

export async function adminGetProducts(params: AdminProductQueryParams = {}): Promise<PaginatedProducts> {
  const { data } = await apiClient.get('/admin/catalog/products', { params })
  return data
}

export async function adminGetProduct(id: string): Promise<Product> {
  const { data } = await apiClient.get(`/admin/catalog/products/${id}`)
  return data
}

export async function adminCreateProduct(payload: ProductCreate): Promise<Product> {
  const { data } = await apiClient.post('/admin/catalog/products', payload)
  return data
}

export async function adminUpdateProduct(id: string, payload: ProductUpdate): Promise<Product> {
  const { data } = await apiClient.put(`/admin/catalog/products/${id}`, payload)
  return data
}

export async function adminDeleteProduct(id: string): Promise<void> {
  await apiClient.delete(`/admin/catalog/products/${id}`)
}

export async function adminGetCategories(): Promise<Category[]> {
  const { data } = await apiClient.get('/admin/catalog/categories')
  return data
}

export async function adminCreateCategory(payload: CategoryCreate): Promise<Category> {
  const { data } = await apiClient.post('/admin/catalog/categories', payload)
  return data
}

export async function adminUpdateCategory(id: string, payload: CategoryUpdate): Promise<Category> {
  const { data } = await apiClient.put(`/admin/catalog/categories/${id}`, payload)
  return data
}

export async function adminDeleteCategory(id: string): Promise<void> {
  await apiClient.delete(`/admin/catalog/categories/${id}`)
}

export async function adminAddProductImage(productId: string, payload: ProductImageCreate): Promise<ProductImage> {
  const { data } = await apiClient.post(`/admin/catalog/products/${productId}/images`, payload)
  return data
}

export async function adminDeleteProductImage(imageId: string): Promise<void> {
  await apiClient.delete(`/admin/catalog/images/${imageId}`)
}
