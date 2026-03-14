export interface RecipeTag {
  id: number
  name: string
}

export interface Recipe {
  id: number
  name: string
  description: string
  ingredients_text: string[]
  instructions: string
  prep_time: number
  cook_time: number
  total_time: number
  servings: number
  difficulty: 'easy' | 'medium' | 'hard'
  cuisine: string
  nutrition_info: Record<string, number>
  tags: RecipeTag[]
  match_score: number
  is_ai_generated: boolean
  is_public: boolean
  created_at: string
  created_by: number
  fork_count: number
  average_rating: number
  review_count: number
}

export interface RecipeFork {
  id: number
  original_recipe: number
  original_recipe_name: string
  custom_ingredients: string[]
  custom_instructions: string
  notes: string
  created_at: string
  updated_at: string
}

export interface MealLog {
  id: number
  recipe: number
  recipe_name: string
  cooked_at: string
  rating: number | null
  notes: string
  used_inventory_only: boolean
  savings_estimate: number | null
}

export interface GenerateRecipePayload {
  use_inventory?: boolean
  inventory_item_ids?: number[]
  inventory_item_quantities?: Record<string, string>
  cuisine_preference?: string
  max_prep_time?: number
  servings?: number
  additional_instructions?: string
  strict_inventory_only?: boolean
}

export interface LogMealPayload {
  rating?: number
  notes?: string
  used_inventory_only?: boolean
  savings_estimate?: number
}

export interface ForkRecipePayload {
  custom_ingredients?: string[]
  custom_instructions?: string
  notes?: string
}

export interface RecipeFilters {
  min_match_score?: number
  difficulty?: string
  is_ai_generated?: boolean
  tags?: number[]
  page?: number
}

export interface RecipeReview {
  id: number
  user: number
  username: string
  recipe: number
  rating: number
  comment: string
  created_at: string
}

export interface ReviewPayload {
  rating: number
  comment?: string
}

export interface GenerationUsage {
  used: number
  limit: number
  remaining: number
  subscription_type: 'free' | 'premium' | 'pro'
}
