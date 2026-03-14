import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TagSelect } from './TagSelect'
import type { InventoryItem, CreateInventoryItemPayload } from '@/types/inventory.types'

const UNITS = [
  'g', 'kg', 'ml', 'L', 'oz', 'lbs', 'cups', 'tbsp', 'tsp', 'pieces',
  'whole', 'slices', 'pinch', 'bunch', 'cans', 'boxes', 'bags', 'jars', 'bottles',
  'cloves', 'sprigs', 'leaves', 'stalks', 'heads', 'packages'
]

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  quantity: z.number().min(0, 'Quantity must be 0 or more'),
  unit: z.string().min(1, 'Unit is required'),
  perishable: z.boolean(),
  expiry_date: z.string().optional().nullable(),
  tag_ids: z.array(z.number()),
})

type FormData = z.infer<typeof schema>

interface InventoryItemFormProps {
  item?: InventoryItem
  onSubmit: (data: CreateInventoryItemPayload) => void
  isLoading?: boolean
}



export function InventoryItemForm({ item, onSubmit, isLoading }: InventoryItemFormProps) {
  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: item?.name ?? '',
      quantity: item?.quantity ?? 1,
      unit: item?.unit ?? 'pieces',
      perishable: item?.perishable ?? false,
      expiry_date: item?.expiry_date ?? null,
      tag_ids: item?.tags?.map((t) => t.id) ?? [],
    },
  })

  useEffect(() => {
    if (item) {
      reset({
        name: item.name,
        quantity: item.quantity,
        unit: item.unit,
        perishable: item.perishable,
        expiry_date: item.expiry_date,
        tag_ids: item.tags.map((t) => t.id),
      })
    }
  }, [item, reset])

  const perishable = watch('perishable')

  const onFormSubmit = (data: FormData) => {
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" {...register('name')} placeholder="e.g. Chicken breast" />
        {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor="quantity">Quantity</Label>
          <Input id="quantity" type="number" step="0.1" {...register('quantity', { valueAsNumber: true })} />
          {errors.quantity && <p className="text-xs text-destructive">{errors.quantity.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="unit">Unit</Label>
          <Controller
            control={control}
            name="unit"
            render={({ field }) => (
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <SelectTrigger id="unit">
                  <SelectValue placeholder="Select unit" />
                </SelectTrigger>
                <SelectContent>
                  {UNITS.map((u) => (
                    <SelectItem key={u} value={u}>{u}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
          {errors.unit && <p className="text-xs text-destructive">{errors.unit.message}</p>}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Controller
          control={control}
          name="perishable"
          render={({ field }) => (
            <Switch checked={field.value} onCheckedChange={field.onChange} id="perishable" />
          )}
        />
        <Label htmlFor="perishable">Perishable</Label>
      </div>

      {perishable && (
        <div className="space-y-2">
          <Label htmlFor="expiry_date">Expiry date</Label>
          <Input id="expiry_date" type="date" {...register('expiry_date')} />
        </div>
      )}

      <div className="space-y-2">
        <Label>Tags</Label>
        <Controller
          control={control}
          name="tag_ids"
          render={({ field }) => (
            <TagSelect value={field.value} onChange={field.onChange} />
          )}
        />
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Saving...' : item ? 'Update item' : 'Add item'}
      </Button>
    </form>
  )
}
