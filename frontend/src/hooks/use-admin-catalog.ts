import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as adminCatalogApi from '@/api/catalog-admin.api'
import { adminCatalogKeys } from '@/lib/query-keys'
import { toast } from 'sonner'
import type { AdminProductQueryParams, ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate, ProductImageCreate } from '@/types/catalog.types'

export function useAdminProducts(params: AdminProductQueryParams = {}) {
  return useQuery({
    queryKey: adminCatalogKeys.products(params),
    queryFn: () => adminCatalogApi.adminGetProducts(params),
    placeholderData: (prev) => prev,
  })
}

export function useAdminProduct(id: string) {
  return useQuery({
    queryKey: adminCatalogKeys.product(id),
    queryFn: () => adminCatalogApi.adminGetProduct(id),
    enabled: !!id,
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: ProductCreate) => adminCatalogApi.adminCreateProduct(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog', 'products'] })
      toast.success('Product created')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ProductUpdate }) =>
      adminCatalogApi.adminUpdateProduct(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog'] })
      toast.success('Product updated')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useDeleteProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => adminCatalogApi.adminDeleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog', 'products'] })
      toast.success('Product deleted')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useAdminCategories() {
  return useQuery({
    queryKey: adminCatalogKeys.categories(),
    queryFn: adminCatalogApi.adminGetCategories,
  })
}

export function useCreateCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CategoryCreate) => adminCatalogApi.adminCreateCategory(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog', 'categories'] })
      toast.success('Category created')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useUpdateCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: CategoryUpdate }) =>
      adminCatalogApi.adminUpdateCategory(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog', 'categories'] })
      toast.success('Category updated')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useDeleteCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => adminCatalogApi.adminDeleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog', 'categories'] })
      toast.success('Category deleted')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useAddProductImage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ productId, payload }: { productId: string; payload: ProductImageCreate }) =>
      adminCatalogApi.adminAddProductImage(productId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog'] })
      toast.success('Image added')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useDeleteProductImage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (imageId: string) => adminCatalogApi.adminDeleteProductImage(imageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'catalog'] })
      toast.success('Image deleted')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
