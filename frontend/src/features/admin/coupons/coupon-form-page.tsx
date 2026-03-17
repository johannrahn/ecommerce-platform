import { useNavigate, useParams } from 'react-router-dom'
import { useForm, type Resolver } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateCoupon, useUpdateCoupon, useAdminCoupon } from '@/hooks/use-admin-coupons'
import { PageHeader } from '@/components/shared/page-header'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { LoadingSpinner } from '@/components/shared/loading-spinner'
import { Loader2 } from 'lucide-react'
import { useEffect } from 'react'

const couponSchema = z.object({
  code: z.string().min(1, 'Code is required').max(50),
  description: z.string().optional(),
  discount_type: z.enum(['percent', 'fixed']),
  discount_value: z.coerce.number().positive(),
  minimum_order_amount: z.coerce.number().min(0).optional(),
  max_discount_amount: z.coerce.number().positive().optional(),
  max_uses: z.coerce.number().int().positive().optional(),
  is_active: z.boolean(),
  one_per_user: z.boolean(),
})

type CouponFormData = z.infer<typeof couponSchema>

export function CouponFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditing = !!id

  const { data: coupon, isLoading } = useAdminCoupon(id ?? '')
  const createCoupon = useCreateCoupon()
  const updateCoupon = useUpdateCoupon()

  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm<CouponFormData>({
    resolver: zodResolver(couponSchema) as unknown as Resolver<CouponFormData>,
    defaultValues: { discount_type: 'percent', is_active: true, one_per_user: false },
  })

  useEffect(() => {
    if (coupon) {
      reset({
        code: coupon.code,
        description: coupon.description ?? '',
        discount_type: coupon.discount_type,
        discount_value: coupon.discount_value,
        minimum_order_amount: coupon.minimum_order_amount ?? undefined,
        max_discount_amount: coupon.max_discount_amount ?? undefined,
        max_uses: coupon.max_uses ?? undefined,
        is_active: coupon.is_active,
        one_per_user: coupon.one_per_user,
      })
    }
  }, [coupon, reset])

  if (isEditing && isLoading) return <LoadingSpinner fullScreen />

  const onSubmit = (data: CouponFormData) => {
    if (isEditing) {
      updateCoupon.mutate({ id: id!, payload: data }, { onSuccess: () => navigate('/admin/coupons') })
    } else {
      createCoupon.mutate(data, { onSuccess: () => navigate('/admin/coupons') })
    }
  }

  const isPending = createCoupon.isPending || updateCoupon.isPending

  return (
    <div className="space-y-6">
      <PageHeader title={isEditing ? 'Edit Coupon' : 'Create Coupon'} />

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="code">Code</Label>
                <Input id="code" {...register('code')} />
                {errors.code && <p className="text-sm text-destructive">{errors.code.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Discount Type</Label>
                <Select
                  defaultValue={coupon?.discount_type ?? 'percent'}
                  onValueChange={(v) => setValue('discount_type', v as 'percent' | 'fixed')}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="percent">Percentage</SelectItem>
                    <SelectItem value="fixed">Fixed Amount</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" rows={2} {...register('description')} />
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor="discount_value">Value</Label>
                <Input id="discount_value" type="number" step="0.01" {...register('discount_value')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="minimum_order_amount">Min. Order</Label>
                <Input id="minimum_order_amount" type="number" step="0.01" {...register('minimum_order_amount')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_discount_amount">Max Discount</Label>
                <Input id="max_discount_amount" type="number" step="0.01" {...register('max_discount_amount')} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_uses">Max Uses</Label>
                <Input id="max_uses" type="number" {...register('max_uses')} />
              </div>
            </div>

            <div className="flex gap-6">
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_active" {...register('is_active')} className="h-4 w-4" />
                <Label htmlFor="is_active">Active</Label>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="one_per_user" {...register('one_per_user')} className="h-4 w-4" />
                <Label htmlFor="one_per_user">One per user</Label>
              </div>
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isEditing ? 'Save Changes' : 'Create Coupon'}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/admin/coupons')}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
