import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { Category } from '@/types/catalog.types'

interface CategoryFilterProps {
  categories: Category[]
  selected: string | undefined
  onSelect: (categoryId: string | undefined) => void
}

export function CategoryFilter({ categories, selected, onSelect }: CategoryFilterProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant={!selected ? 'default' : 'outline'}
        size="sm"
        onClick={() => onSelect(undefined)}
      >
        All
      </Button>
      {categories.map((cat) => (
        <Button
          key={cat.id}
          variant={selected === cat.id ? 'default' : 'outline'}
          size="sm"
          onClick={() => onSelect(cat.id)}
          className={cn(selected === cat.id && 'bg-primary')}
        >
          {cat.name}
        </Button>
      ))}
    </div>
  )
}
