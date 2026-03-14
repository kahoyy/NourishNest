import { useState } from 'react'
import { Clock, ChefHat, Users, Utensils, Star } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { MatchScoreBadge } from './MatchScoreBadge'
import { NutritionBadge } from './NutritionBadge'
import { LogMealDialog } from './LogMealDialog'
import { ForkRecipeDialog } from './ForkRecipeDialog'
import { useAuth } from '@/context/AuthContext'
import { useTogglePublic, useReviews, useCreateReview } from '@/hooks/useRecipes'
import type { Recipe } from '@/types/recipe.types'

const reviewSchema = z.object({
  rating: z.number().min(1).max(5),
  comment: z.string().optional(),
})

type ReviewFormData = z.infer<typeof reviewSchema>

interface RecipeDetailPanelProps {
  recipe: Recipe
  showActions?: boolean
}

export function RecipeDetailPanel({ recipe, showActions = true }: RecipeDetailPanelProps) {
  const [logOpen, setLogOpen] = useState(false)
  const [forkOpen, setForkOpen] = useState(false)
  const [confirmPublicOpen, setConfirmPublicOpen] = useState(false)

  const { user } = useAuth()
  const togglePublicMutation = useTogglePublic()
  const { data: reviews = [] } = useReviews(recipe.id)
  const createReviewMutation = useCreateReview()

  const { register, handleSubmit, setValue, watch, reset, formState: { isSubmitting } } = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
    defaultValues: { rating: 5, comment: '' },
  })

  const rating = watch('rating')

  const handleToggleClick = (checked: boolean) => {
    if (checked && !recipe.is_public) {
      setConfirmPublicOpen(true)
    } else if (!checked && recipe.is_public) {
      togglePublicMutation.mutate({ id: recipe.id, isPublic: false })
    }
  }

  const confirmPublic = () => {
    togglePublicMutation.mutate({ id: recipe.id, isPublic: true })
    setConfirmPublicOpen(false)
  }

  const onReviewSubmit = async (data: ReviewFormData) => {
    await createReviewMutation.mutateAsync({ id: recipe.id, data })
    reset()
  }

  const isOwner = user?.id === recipe.created_by
  const hasReviewed = reviews.some((r: any) => r.user === user?.id)

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h1 className="text-3xl font-bold">{recipe.name}</h1>
          <MatchScoreBadge score={recipe.match_score} />
        </div>
        <p className="mt-2 text-muted-foreground">{recipe.description}</p>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            Prep: {recipe.prep_time} min
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            Cook: {recipe.cook_time} min
          </span>
          <span className="flex items-center gap-1">
            <ChefHat className="h-4 w-4" />
            <span className="capitalize">{recipe.difficulty}</span>
          </span>
          <span className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            {recipe.servings} servings
          </span>
          {recipe.cuisine && (
            <span className="flex items-center gap-1">
              <Utensils className="h-4 w-4" />
              {recipe.cuisine}
            </span>
          )}
        </div>
        {recipe.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {recipe.tags.map((tag) => (
              <Badge key={tag.id} variant="secondary">
                {tag.name}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <Separator />

      {/* Ingredients */}
      <div>
        <h2 className="mb-3 text-xl font-semibold">Ingredients</h2>
        <ul className="space-y-1 text-sm">
          {recipe.ingredients_text.map((ing, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
              {ing}
            </li>
          ))}
        </ul>
      </div>

      <Separator />

      {/* Instructions */}
      <div>
        <h2 className="mb-3 text-xl font-semibold">Instructions</h2>
        <div className="space-y-3 text-sm">
          {recipe.instructions.split('\n').filter(Boolean).map((step, i) => (
            <div key={i} className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                {i + 1}
              </span>
              <p className="leading-relaxed">{step}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Nutrition */}
      {Object.keys(recipe.nutrition_info).length > 0 && (
        <>
          <Separator />
          <div>
            <h2 className="mb-3 text-xl font-semibold">Nutrition</h2>
            <NutritionBadge nutritionInfo={recipe.nutrition_info} />
          </div>
        </>
      )}

      {/* Actions */}
      {showActions && (
        <>
          <Separator />
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={() => setLogOpen(true)}>Log meal</Button>
            <Button variant="outline" onClick={() => setForkOpen(true)}>
              Fork recipe
            </Button>
            <div className="flex items-center gap-2">
              <Switch
                id="public-toggle"
                checked={recipe.is_public}
                onCheckedChange={handleToggleClick}
                disabled={togglePublicMutation.isPending}
              />
              <Label htmlFor="public-toggle" className="text-sm">
                {recipe.is_public ? 'Public' : 'Private'}
              </Label>
            </div>
          </div>
        </>
      )}

      {/* Reviews Section (Only if public or has reviews) */}
      {(recipe.is_public || reviews.length > 0) && (
        <>
          <Separator />
          <div>
            <h2 className="mb-4 text-xl font-semibold">Reviews</h2>
            
            {!isOwner && recipe.is_public && !hasReviewed && (
              <form onSubmit={handleSubmit(onReviewSubmit)} className="mb-6 space-y-3 rounded-lg border bg-card p-4">
                <h3 className="text-sm font-medium">Leave a Review</h3>
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setValue('rating', star)}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`h-5 w-5 ${
                          star <= rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-muted-foreground'
                        }`}
                      />
                    </button>
                  ))}
                </div>
                <Textarea
                  {...register('comment')}
                  placeholder="What did you think of this recipe?"
                  rows={2}
                  className="resize-none"
                />
                <Button type="submit" size="sm" disabled={isSubmitting || createReviewMutation.isPending}>
                  {createReviewMutation.isPending ? 'Posting...' : 'Post Review'}
                </Button>
              </form>
            )}

            <div className="space-y-4">
              {reviews.length === 0 ? (
                <p className="text-sm text-muted-foreground">No reviews yet.</p>
              ) : (
                reviews.map((r: any) => (
                  <div key={r.id} className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{r.username}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(r.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                      <div className="flex items-center ml-auto">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400 mr-1" />
                        <span className="text-xs font-medium">{r.rating}</span>
                      </div>
                    </div>
                    {r.comment && <p className="text-sm text-muted-foreground">{r.comment}</p>}
                    <Separator className="mt-4" />
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      {/* Public Confirmation Dialog */}
      <Dialog open={confirmPublicOpen} onOpenChange={setConfirmPublicOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Post this recipe on community?</DialogTitle>
            <DialogDescription>
              This will make your recipe visible to all users. They will be able to fork it and leave reviews.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setConfirmPublicOpen(false)}>
              Cancel
            </Button>
            <Button onClick={confirmPublic} disabled={togglePublicMutation.isPending}>
              {togglePublicMutation.isPending ? 'Posting...' : 'Yes, post it'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <LogMealDialog
        open={logOpen}
        onOpenChange={setLogOpen}
        recipeId={recipe.id}
        recipeName={recipe.name}
      />
      <ForkRecipeDialog open={forkOpen} onOpenChange={setForkOpen} recipe={recipe} />
    </div>
  )
}
