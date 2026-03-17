export interface AuditLog {
  id: string
  admin_user_id: string
  action: string
  entity_type: string
  entity_id: string
  metadata_json: string | null
  created_at: string
}

export interface PaginatedAuditLogs {
  items: AuditLog[]
  total: number
  limit: number
  offset: number
}

export interface AuditQueryParams {
  limit?: number
  offset?: number
  action?: string
  entity_type?: string
}
