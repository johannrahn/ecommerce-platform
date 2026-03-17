import { useQuery } from '@tanstack/react-query'
import * as auditApi from '@/api/audit-admin.api'
import { adminAuditKeys } from '@/lib/query-keys'
import type { AuditQueryParams } from '@/types/audit.types'

export function useAuditLogs(params: AuditQueryParams = {}) {
  return useQuery({
    queryKey: adminAuditKeys.list(params),
    queryFn: () => auditApi.adminGetAuditLogs(params),
    placeholderData: (prev) => prev,
  })
}
