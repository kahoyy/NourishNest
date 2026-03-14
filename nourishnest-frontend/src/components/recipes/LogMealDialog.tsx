import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Star } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { useLogMeal } from '@/hooks/useMealHistory'
import { cn } from '@/lib/utils'

const schema = z.object({
  rating: z.number().min(1).max(5).optional(),
  notes: z.string().optional(),
  used_inventory_only: z.boolean(),
  savings_estimate: z.preprocess(
    (val) => {
      if (val === '' || val === undefined || val === null) return undefined;
      const parsed = Number(val);
      return Number.isNaN(parsed) ? undefined : parsed;
    },
    z.number().min(0).optional()
  ),
})

type FormData = z.infer<typeof schema>

interface LogMealDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  recipeId: number
  recipeName: string
}

export function LogMealDialog({ open, onOpenChange, recipeId, recipeName }: LogMealDialogProps) {
  const logMutation = useLogMeal()
  const [hovered, setHovered] = useState(0)

  const { handleSubmit, control, register, formState: { isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { used_inventory_only: false },
  })

  const onSubmit = async (data: FormData) => {
    await logMutation.mutateAsync({ id: recipeId, data })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Log meal: {recipeName}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Star rating */}
          <div className="space-y-2">
            <Label>Rating (optional)</Label>
            <Controller
              control={control}
              name="rating"
              render={({ field }) => (
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onMouseEnter={() => setHovered(star)}
                      onMouseLeave={() => setHovered(0)}
                      onClick={() => field.onChange(star === field.value ? undefined : star)}
                    >
                      <Star
                        className={cn(
                          'h-6 w-6 transition-colors',
                          (hovered || (field.value ?? 0)) >= star
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-muted-foreground'
                        )}
                      />
                    </button>
                  ))}
                </div>
              )}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes (optional)</Label>
            <Textarea id="notes" {...register('notes')} placeholder="How did it turn out?" />
          </div>

          <div className="flex items-center gap-3">
            <Controller
              control={control}
              name="used_inventory_only"
              render={({ field }) => (
                <Switch checked={field.value} onCheckedChange={field.onChange} id="inventory-only" />
              )}
            />
            <Label htmlFor="inventory-only">Used pantry items only</Label>
          </div>

          <div className="space-y-2">
            <Label htmlFor="savings">Estimated savings ($, optional)</Label>
            <Input id="savings" type="number" step="0.01" min="0" {...register('savings_estimate')} />
          </div>

          <Button type="submit" className="w-full" disabled={isSubmitting || logMutation.isPending}>
            {logMutation.isPending ? 'Logging...' : 'Log meal'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
