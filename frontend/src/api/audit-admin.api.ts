import apiClient from '@/lib/api-client'
import type { PaginatedAuditLogs, AuditQueryParams } from '@/types/audit.types'

export async function adminGetAuditLogs(params: AuditQueryParams = {}): Promise<PaginatedAuditLogs> {
  const { data } = await apiClient.get('/admin/audit-logs', { params })
  return data
}
