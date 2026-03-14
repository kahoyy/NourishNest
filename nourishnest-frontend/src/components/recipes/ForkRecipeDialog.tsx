import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useForkRecipe } from '@/hooks/useRecipes'
import type { Recipe } from '@/types/recipe.types'

const schema = z.object({
  custom_ingredients: z.string().optional(),
  custom_instructions: z.string().optional(),
  notes: z.string().optional(),
})

type FormData = z.infer<typeof schema>

interface ForkRecipeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  recipe: Recipe
}

export function ForkRecipeDialog({ open, onOpenChange, recipe }: ForkRecipeDialogProps) {
  const forkMutation = useForkRecipe()

  const { handleSubmit, register, formState: { isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { 
      custom_ingredients: recipe.ingredients_text.join('\n'),
      custom_instructions: recipe.instructions, 
      notes: '' 
    },
  })

  const onSubmit = async (data: FormData) => {
    await forkMutation.mutateAsync({
      id: recipe.id,
      data: {
        custom_ingredients: data.custom_ingredients ? data.custom_ingredients.split('\n').filter(i => i.trim()) : [],
        custom_instructions: data.custom_instructions,
        notes: data.notes,
      },
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Fork: {recipe.name}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="custom_ingredients">Custom ingredients (one per line)</Label>
            <Textarea
              id="custom_ingredients"
              {...register('custom_ingredients')}
              rows={4}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="custom_instructions">Custom instructions</Label>
            <Textarea
              id="custom_instructions"
              {...register('custom_instructions')}
              rows={6}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea id="notes" {...register('notes')} placeholder="Why are you forking this?" />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || forkMutation.isPending}
          >
            {forkMutation.isPending ? 'Forking...' : 'Fork recipe'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
