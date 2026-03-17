export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  is_active: boolean
  created_at: string
}

export interface CategoryCreate {
  name: string
  slug: string
  description?: string
}

export interface CategoryUpdate {
  name?: string
  slug?: string
  description?: string
  is_active?: boolean
}

export interface ProductImage {
  id: string
  url: string
  is_primary: boolean
  sort_order: number
}

export interface ProductImageCreate {
  url: string
  is_primary?: boolean
  sort_order?: number
}

export interface Product {
  id: string
  name: string
  slug: string
  description: string | null
  price: number
  stock: number
  category_id: string
  category: Category
  images: ProductImage[]
  is_active: boolean
  average_rating: number | null
  reviews_count: number
  created_at: string
  updated_at: string
}

export interface ProductListItem {
  id: string
  name: string
  slug: string
  price: number
  stock: number
  category: Category
  primary_image: string | null
  is_active: boolean
  average_rating: number | null
  reviews_count: number
}

export interface PaginatedProducts {
  items: ProductListItem[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ProductCreate {
  name: string
  slug: string
  description?: string
  price: number
  stock?: number
  category_id: string
  images?: ProductImageCreate[]
}

export interface ProductUpdate {
  name?: string
  slug?: string
  description?: string
  price?: number
  stock?: number
  category_id?: string
  is_active?: boolean
}

export interface ProductQueryParams {
  page?: number
  per_page?: number
  category_id?: string
  search?: string
}

export interface AdminProductQueryParams {
  page?: number
  per_page?: number
  search?: string
}
