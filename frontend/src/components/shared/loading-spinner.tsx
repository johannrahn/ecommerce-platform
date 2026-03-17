import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  className?: string
  fullScreen?: boolean
}

export function LoadingSpinner({ className, fullScreen }: LoadingSpinnerProps) {
  if (fullScreen) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className={cn('h-8 w-8 animate-spin text-primary', className)} />
      </div>
    )
  }

  return <Loader2 className={cn('h-6 w-6 animate-spin text-primary', className)} />
}
