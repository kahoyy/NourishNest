import type { InventoryFilters } from '@/types/inventory.types'
import type { RecipeFilters } from '@/types/recipe.types'

export const queryKeys = {
  currentUser:        (): string[] => ['users', 'me'],
  userProfile:        (): string[] => ['users', 'profile'],
  userRewards:        (): string[] => ['users', 'rewards'],
  inventoryItems:     (filters?: InventoryFilters) => ['inventory', 'items', filters ?? {}] as const,
  inventoryTags:      (): string[] => ['inventory', 'tags'],
  inventoryHistory:   (): string[] => ['inventory', 'history'],
  recipes:            (filters?: RecipeFilters) => ['recipes', 'list', filters ?? {}] as const,
  recipe:             (id: number) => ['recipes', 'detail', id] as const,
  recipeReviews:      (id: number) => ['recipes', 'detail', id, 'reviews'] as const,
  myForks:            (): string[] => ['recipes', 'forks'],
  fork:               (id: number) => ['recipes', 'forks', id] as const,
  mealHistory:        (): string[] => ['recipes', 'history'],
  generationUsage:    (): string[] => ['recipes', 'generationUsage'],
  communityRecipes:   (filters?: Record<string, unknown>) => ['community', 'list', filters ?? {}] as const,
  communityRecipe:    (id: number) => ['community', 'detail', id] as const,
  popularRecipes:     (): string[] => ['community', 'popular'],
  subscriptionPlans:  (): string[] => ['subscription', 'plans'],
  subscriptionStatus: (): string[] => ['subscription', 'status'],
  transactions:       (): string[] => ['subscription', 'transactions'],
  nutritionAnalytics: (days: number) => ['analytics', 'nutrition', days] as const,
  inventoryAnalytics: (): string[] => ['analytics', 'inventory'],
}
