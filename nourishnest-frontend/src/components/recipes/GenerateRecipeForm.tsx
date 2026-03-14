import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm, Controller, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Checkbox } from '@/components/ui/checkbox'
import { Plus, AlertTriangle } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'
import { cn } from '@/lib/utils'
import { useGenerateRecipe, useGenerationUsage } from '@/hooks/useRecipes'
import { useInventoryItems, useCreateInventoryItem } from '@/hooks/useInventory'
import { InventoryItemForm } from '@/components/inventory/InventoryItemForm'

const schema = z.object({
  use_inventory: z.boolean(),
  strict_inventory_only: z.boolean().optional(),
  inventory_item_ids: z.array(z.number()),
  inventory_item_quantities: z.record(z.string(), z.string()),
  cuisine_preference: z.string().optional(),
  max_prep_time: z.number().min(5).max(480).optional(),
  servings: z.number().min(1).max(20),
  additional_instructions: z.string().optional(),
})

type FormData = z.infer<typeof schema>

export function GenerateRecipeForm() {
  const navigate = useNavigate()
  const [dialogOpen, setDialogOpen] = useState(false)
  const generateMutation = useGenerateRecipe()
  const createMutation = useCreateInventoryItem()
  const { data: usageData } = useGenerationUsage()
  const { data: inventoryData } = useInventoryItems()
  const inventoryItems = inventoryData?.results ?? []

  const { register, handleSubmit, control, watch, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      use_inventory: true,
      strict_inventory_only: false,
      inventory_item_ids: [],
      inventory_item_quantities: {},
      servings: 2,
    },
  })

  const useInventory = watch('use_inventory')
  const selectedIds = useWatch({ control, name: 'inventory_item_ids' })
  const quantities = useWatch({ control, name: 'inventory_item_quantities' })

  const handleItemToggle = (itemId: number, itemQuantity: string, checked: boolean) => {
    const currentIds = selectedIds ?? []
    const currentQtys = quantities ?? {}

    if (checked) {
      setValue('inventory_item_ids', [...currentIds, itemId])
      // Pre-fill with the stored quantity as the default override value
      setValue('inventory_item_quantities', {
        ...currentQtys,
        [String(itemId)]: itemQuantity,
      })
    } else {
      setValue('inventory_item_ids', currentIds.filter((id) => id !== itemId))
      // Remove override entry when item is unchecked
      const updated = { ...currentQtys }
      delete updated[String(itemId)]
      setValue('inventory_item_quantities', updated)
    }
  }

  const onSubmit = async (data: FormData) => {
    try {
      const hasQuantities = Object.keys(data.inventory_item_quantities).length > 0
      const recipe = await generateMutation.mutateAsync({
        use_inventory: data.use_inventory,
        strict_inventory_only: data.strict_inventory_only,
        inventory_item_ids: data.use_inventory ? data.inventory_item_ids : undefined,
        inventory_item_quantities:
          data.use_inventory && hasQuantities ? data.inventory_item_quantities : undefined,
        cuisine_preference: data.cuisine_preference || undefined,
        max_prep_time: data.max_prep_time || undefined,
        servings: data.servings,
        additional_instructions: data.additional_instructions || undefined,
      })
      navigate(`/recipes/${recipe.id}`)
    } catch (err: unknown) {
      const status = (err as { response?: { status: number } })?.response?.status
      if (status === 429) {
        toast.error(
          <span>
            Daily generation limit reached.{' '}
            <Link to="/subscription" className="underline">
              Upgrade your plan
            </Link>
          </span>
        )
      }
    }
  }

  if (generateMutation.isPending) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <LoadingSpinner size="lg" />
        <p className="text-lg font-medium">Generating your recipe...</p>
        <p className="text-sm text-muted-foreground">This can take 5-15 seconds</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-xl">
      {usageData && (() => {
        const pct = (usageData.used / usageData.limit) * 100
        const isWarning = pct >= 70 && pct < 100
        const isAtLimit = usageData.remaining === 0
        const planLabel: Record<string, string> = { free: 'Free', premium: 'Premium', pro: 'Pro' }

        return (
          <div className="rounded-lg border p-4 space-y-2 bg-muted/40">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {usageData.used} of {usageData.limit} generations used today
              </span>
              <Badge variant={isAtLimit ? 'destructive' : 'secondary'}>
                {planLabel[usageData.subscription_type] ?? usageData.subscription_type} Plan
              </Badge>
            </div>
            <Progress
              value={pct}
              className={cn(
                'h-2',
                isAtLimit ? '[&>div]:bg-destructive' :
                isWarning  ? '[&>div]:bg-yellow-500'  :
                             '[&>div]:bg-green-500'
              )}
            />
            {(isWarning || isAtLimit) && (
              <div className="flex items-center gap-2 text-xs">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-yellow-500" />
                {isAtLimit ? (
                  <span>
                    Limit reached.{' '}
                    <Link to="/subscription" className="underline font-medium">Upgrade your plan</Link>
                    {' '}for more generations.
                  </span>
                ) : (
                  <span>
                    {usageData.remaining} generation{usageData.remaining !== 1 ? 's' : ''} left.{' '}
                    <Link to="/subscription" className="underline font-medium">Upgrade</Link> for more.
                  </span>
                )}
              </div>
            )}
          </div>
        )
      })()}

      {/* Pantry toggle */}
      <div className="flex items-center gap-3">
        <Controller
          control={control}
          name="use_inventory"
          render={({ field }) => (
            <Switch checked={field.value} onCheckedChange={field.onChange} id="use-inventory" />
          )}
        />
        <Label htmlFor="use-inventory">Use my pantry ingredients</Label>
      </div>

      {useInventory && (
        <div className="flex items-center gap-3 ml-6 mb-4">
          <Controller
            control={control}
            name="strict_inventory_only"
            render={({ field }) => (
              <Switch checked={field.value} onCheckedChange={field.onChange} id="strict-inventory-only" />
            )}
          />
          <Label htmlFor="strict-inventory-only">Strictly use only these items (no outside ingredients)</Label>
        </div>
      )}

      {/* Pantry item list with per-item quantity override */}
      {useInventory && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Select specific items (optional — leave blank to use all)</Label>
            <Button type="button" variant="outline" size="sm" onClick={() => setDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Item
            </Button>
          </div>
          {inventoryItems.length > 0 ? (
            <>
              <div className="max-h-64 overflow-y-auto rounded border p-3 space-y-3">
                {inventoryItems.map((item) => {
                  const isChecked = (selectedIds ?? []).includes(item.id)
                  const storedQty = item.quantity
                  return (
                    <div key={item.id} className="flex items-center gap-3">
                      <Checkbox
                        id={`item-${item.id}`}
                        checked={isChecked}
                        onCheckedChange={(checked) =>
                          handleItemToggle(item.id, String(storedQty), !!checked)
                        }
                      />
                      <label
                        htmlFor={`item-${item.id}`}
                        className="text-sm cursor-pointer flex-1 min-w-0 truncate"
                      >
                        {item.name}
                        {!isChecked && (
                          <span className="text-muted-foreground ml-1">({storedQty} {item.unit})</span>
                        )}
                      </label>

                      {isChecked && (
                        <div className="flex items-center gap-1 shrink-0">
                          <span className="text-xs text-muted-foreground">Qty:</span>
                          <Input
                            className="h-7 w-28 text-sm px-2"
                            value={(quantities ?? {})[String(item.id)] ?? storedQty}
                            onChange={(e) => {
                              setValue('inventory_item_quantities', {
                                ...(quantities ?? {}),
                                [String(item.id)]: e.target.value,
                              })
                            }}
                            placeholder={String(storedQty)}
                            aria-label={`Quantity for ${item.name}`}
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
              {(selectedIds ?? []).length > 0 && (
                <p className="text-xs text-muted-foreground">
                  You can adjust the quantity for each selected item above.
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground italic border rounded p-4 text-center">Your pantry is empty.</p>
          )}
        </div>
      )}

      {/* Cuisine preference */}
      <div className="space-y-2">
        <Label htmlFor="cuisine_preference">Cuisine preference (optional)</Label>
        <Input
          id="cuisine_preference"
          {...register('cuisine_preference')}
          placeholder="e.g. Italian, Mexican, Asian"
        />
      </div>

      {/* Prep time & servings */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="max_prep_time">Max prep time (minutes)</Label>
          <Input
            id="max_prep_time"
            type="number"
            min={5}
            max={480}
            {...register('max_prep_time', { valueAsNumber: true })}
            placeholder="e.g. 30"
          />
          {errors.max_prep_time && (
            <p className="text-xs text-destructive">{errors.max_prep_time.message}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="servings">Servings</Label>
          <Input
            id="servings"
            type="number"
            min={1}
            max={20}
            {...register('servings', { valueAsNumber: true })}
          />
          {errors.servings && (
            <p className="text-xs text-destructive">{errors.servings.message}</p>
          )}
        </div>
      </div>

      {/* Additional instructions */}
      <div className="space-y-2">
        <Label htmlFor="additional_instructions">Additional instructions (optional)</Label>
        <Textarea
          id="additional_instructions"
          {...register('additional_instructions')}
          placeholder="e.g. Make it vegetarian, low-calorie, kid-friendly..."
          rows={3}
        />
      </div>

      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={generateMutation.isPending || usageData?.remaining === 0}
      >
        {usageData?.remaining === 0 ? 'Generation Limit Reached' : 'Generate Recipe'}
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add item to pantry</DialogTitle>
          </DialogHeader>
          <InventoryItemForm
            onSubmit={(data) => {
              createMutation.mutate(data, {
                onSuccess: () => setDialogOpen(false),
              })
            }}
            isLoading={createMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </form>
  )
}
