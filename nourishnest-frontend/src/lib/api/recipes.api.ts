import { apiClient } from './client'
import type {
  Recipe,
  RecipeFork,
  MealLog,
  GenerateRecipePayload,
  LogMealPayload,
  ForkRecipePayload,
  RecipeFilters,
  RecipeReview,
  ReviewPayload,
  GenerationUsage,
} from '@/types/recipe.types'
import type { PaginatedResponse } from '@/types/inventory.types'

export const recipesApi = {
  getRecipes: async (filters?: RecipeFilters): Promise<PaginatedResponse<Recipe>> => {
    const params: Record<string, unknown> = {}
    if (filters?.min_match_score !== undefined) params.min_match_score = filters.min_match_score
    if (filters?.difficulty) params.difficulty = filters.difficulty
    if (filters?.is_ai_generated !== undefined) params.is_ai_generated = filters.is_ai_generated
    if (filters?.tags?.length) params.tags = filters.tags.join(',')
    if (filters?.page) params.page = filters.page
    const res = await apiClient.get('/recipes/', { params })
    return res.data
  },

  getRecipe: async (id: number): Promise<Recipe> => {
    const res = await apiClient.get(`/recipes/${id}/`)
    return res.data
  },

  generateRecipe: async (data: GenerateRecipePayload): Promise<Recipe> => {
    const res = await apiClient.post('/recipes/generate/', data)
    return res.data
  },

  togglePublic: async (id: number, isPublic: boolean): Promise<Recipe> => {
    const res = await apiClient.patch(`/recipes/${id}/`, { is_public: isPublic })
    return res.data
  },

  forkRecipe: async (id: number, data: ForkRecipePayload): Promise<RecipeFork> => {
    const res = await apiClient.post(`/recipes/${id}/fork/`, data)
    return res.data
  },

  getMyForks: async (): Promise<PaginatedResponse<RecipeFork>> => {
    const res = await apiClient.get('/recipes/my-forks/')
    return res.data
  },

  getFork: async (id: number): Promise<RecipeFork> => {
    const res = await apiClient.get(`/recipes/my-forks/${id}/`)
    return res.data
  },

  logMeal: async (id: number, data: LogMealPayload): Promise<MealLog & { points_earned?: number }> => {
    const res = await apiClient.post(`/recipes/${id}/log_meal/`, data)
    return res.data
  },

  getMealHistory: async (): Promise<PaginatedResponse<MealLog>> => {
    const res = await apiClient.get('/recipes/history/')
    return res.data
  },

  getReviews: async (id: number): Promise<RecipeReview[]> => {
    const res = await apiClient.get(`/recipes/${id}/reviews/`)
    return res.data
  },

  createReview: async (id: number, data: ReviewPayload): Promise<RecipeReview> => {
    const res = await apiClient.post(`/recipes/${id}/reviews/`, data)
    return res.data
  },

  getGenerationUsage: async (): Promise<GenerationUsage> => {
    const res = await apiClient.get('/recipes/generation-usage/')
    return res.data
  },
}
