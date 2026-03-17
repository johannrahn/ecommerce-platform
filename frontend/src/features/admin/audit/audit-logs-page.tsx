import { useState } from 'react'
import { useAuditLogs } from '@/hooks/use-admin-audit'
import { PageHeader } from '@/components/shared/page-header'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { LoadingSpinner } from '@/components/shared/loading-spinner'
import { formatDateTime } from '@/lib/utils'

export function AuditLogsPage() {
  const [offset, setOffset] = useState(0)
  const limit = 20
  const { data, isLoading } = useAuditLogs({ limit, offset })

  return (
    <div className="space-y-6">
      <PageHeader title="Audit Logs" description="Admin action history" />

      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Action</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>Entity ID</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="font-medium">{log.action}</TableCell>
                    <TableCell>{log.entity_type}</TableCell>
                    <TableCell className="font-mono text-sm">{log.entity_id.slice(0, 8)}</TableCell>
                    <TableCell>{formatDateTime(log.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {data && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Showing {offset + 1}-{Math.min(offset + limit, data.total)} of {data.total}
              </span>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>
                  Previous
                </Button>
                <Button variant="outline" size="sm" disabled={offset + limit >= data.total} onClick={() => setOffset(offset + limit)}>
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
