export interface ApiError {
  status: number
  message: string
}

export interface PaginationParams {
  page?: number
  per_page?: number
}
