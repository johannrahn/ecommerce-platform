import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="font-serif text-8xl font-semibold text-muted-foreground/20">404</h1>
      <p className="mt-2 text-lg text-muted-foreground">Page not found</p>
      <p className="mt-1 text-sm text-muted-foreground/60">The page you're looking for doesn't exist or has been moved.</p>
      <Button className="mt-8" asChild>
        <Link to="/">Go Home</Link>
      </Button>
    </div>
  )
}
