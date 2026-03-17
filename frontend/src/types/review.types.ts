export interface Review {
  id: string
  user_id: string
  user_name: string
  product_id: string
  rating: number
  title: string | null
  comment: string | null
  is_visible: boolean
  created_at: string
  updated_at: string
}

export interface ReviewCreate {
  rating: number
  title?: string
  comment?: string
}

export interface ReviewUpdate {
  rating?: number
  title?: string
  comment?: string
}
