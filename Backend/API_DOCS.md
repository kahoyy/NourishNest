# NourishNest API Documentation

**Base URL:** `http://localhost:8000/api/v1/`  
**Authentication:** JWT Bearer Token  
**Content-Type:** `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Profile](#user-profile)
3. [Inventory](#inventory)
4. [Recipes](#recipes)
5. [Analytics](#analytics-premium)
6. [Subscription](#subscription)
7. [Community](#community)
8. [Rewards and History](#rewards-and-history)

---

## Authentication

### Register

Create a new user account.

```
POST /auth/register/
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "subscription_type": "free",
    "health_profile": {},
    "is_premium": false,
    "date_joined": "2026-02-16T10:00:00Z",
    "last_login": null
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

### Login

Authenticate and receive JWT tokens.

```
POST /auth/login/
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### Refresh Token

Get a new access token using refresh token.

```
POST /auth/token/refresh/
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `200 OK`

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### Logout

Invalidate refresh token.

```
POST /auth/logout/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `200 OK`

```json
{
  "message": "Successfully logged out"
}
```

---

## User Profile

### Get Current User

```
GET /users/me/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "subscription_type": "free",
  "health_profile": {
    "allergies": ["peanuts", "shellfish"],
    "dietary_restrictions": ["vegetarian"],
    "health_goals": ["weight_loss"],
    "calorie_target": 2000
  },
  "is_premium": false,
  "date_joined": "2026-02-16T10:00:00Z",
  "last_login": "2026-02-16T12:00:00Z"
}
```

---

### Update Profile

```
PATCH /users/me/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "first_name": "Johnny",
  "health_profile": {
    "allergies": ["peanuts"],
    "dietary_restrictions": ["vegan"],
    "health_goals": ["muscle_gain"],
    "preferred_cuisines": ["italian", "asian"],
    "disliked_ingredients": ["cilantro"],
    "calorie_target": 2500
  }
}
```

**Response:** `200 OK`

---

## Inventory

### List Inventory Items

```
GET /inventory/
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `perishable` | boolean | Filter by perishable status |
| `tags` | integer[] | Filter by dietary tag IDs |
| `expired` | boolean | Filter expired items |

**Example:** `GET /inventory/?perishable=true&tags=1&tags=2`

**Response:** `200 OK`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Chicken Breast",
      "quantity": "500g",
      "perishable": true,
      "expiry_date": "2026-02-20",
      "tags": [
        { "id": 1, "name": "Protein", "description": "High protein foods" }
      ],
      "notes": "Organic, free-range",
      "is_expired": false,
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-15T10:00:00Z"
    }
  ]
}
```

---

### Add Inventory Item

```
POST /inventory/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Chicken Breast",
  "quantity": "500g",
  "perishable": true,
  "expiry_date": "2026-02-20",
  "tag_ids": [1, 3],
  "notes": "Organic, free-range"
}
```

**Response:** `201 Created`

---

### Get Single Item

```
GET /inventory/{id}/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

---

### Update Item

```
PATCH /inventory/{id}/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "quantity": "300g",
  "notes": "Used some for dinner"
}
```

**Response:** `200 OK`

---

### Delete Item

```
DELETE /inventory/{id}/
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### Undo Last Action

Undo the last inventory action (LIFO stack).

```
POST /inventory/undo/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "message": "Restored item: Chicken Breast",
  "item": {
    "id": 5,
    "name": "Chicken Breast",
    "quantity": "500g",
    ...
  }
}
```

---

### View Action History

```
GET /inventory/history/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "action_type": "add",
    "model_affected": "InventoryItem",
    "object_id": 5,
    "metadata": { "old_data": {}, "action": "add" },
    "timestamp": "2026-02-16T10:00:00Z",
    "is_undone": false
  }
]
```

---

### List Dietary Tags

```
GET /inventory/tags/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
[
  { "id": 1, "name": "Protein", "description": "High protein foods" },
  { "id": 2, "name": "Vegan", "description": "Plant-based ingredients" },
  { "id": 3, "name": "Gluten-Free", "description": "No gluten" }
]
```

---

## Recipes

### List Recipes

```
GET /recipes/
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `min_score` | float | Minimum match score (0-1) |
| `tags` | integer[] | Filter by dietary tag IDs |
| `difficulty` | string | `easy`, `medium`, `hard` |
| `ai_generated` | boolean | Filter by AI-generated status |

**Response:** `200 OK`

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Grilled Chicken Salad",
      "description": "A healthy, protein-packed salad",
      "tags": [{ "id": 1, "name": "Protein" }],
      "match_score": 0.85,
      "total_time_minutes": 25,
      "servings": 2,
      "difficulty": "easy",
      "is_public": false,
      "created_at": "2026-02-16T10:00:00Z"
    }
  ]
}
```

---

### Get Recipe Details

```
GET /recipes/{id}/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "Grilled Chicken Salad",
  "description": "A healthy, protein-packed salad",
  "instructions": "Step 1: Season the chicken...\nStep 2: Grill for 6 minutes...",
  "ingredients_text": [
    "500g chicken breast",
    "2 cups mixed greens",
    "1/4 cup olive oil",
    "1 lemon, juiced"
  ],
  "tags": [{ "id": 1, "name": "Protein" }],
  "generated_by_llm": true,
  "nutrition_info": {
    "calories": 350,
    "protein_g": 42,
    "carbs_g": 8,
    "fat_g": 18,
    "fiber_g": 3
  },
  "match_score": 0.85,
  "prep_time_minutes": 10,
  "cook_time_minutes": 15,
  "total_time_minutes": 25,
  "servings": 2,
  "difficulty": "easy",
  "is_public": false,
  "created_by": 1,
  "created_by_username": "johndoe",
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:00:00Z"
}
```

---

### Generate Recipe with AI

Generate a recipe based on inventory and health profile.

```
POST /recipes/generate/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "use_inventory": true,
  "inventory_item_ids": [1, 2, 3],
  "cuisine_preference": "Italian",
  "max_prep_time": 30,
  "servings": 4,
  "additional_instructions": "Make it kid-friendly"
}
```

| Field                     | Type      | Required | Description                                        |
| ------------------------- | --------- | -------- | -------------------------------------------------- |
| `use_inventory`           | boolean   | No       | Use items from inventory (default: true)           |
| `inventory_item_ids`      | integer[] | No       | Specific items to use (all non-expired if omitted) |
| `cuisine_preference`      | string    | No       | Preferred cuisine type                             |
| `max_prep_time`           | integer   | No       | Max prep time in minutes (5-480)                   |
| `servings`                | integer   | No       | Number of servings (default: 2)                    |
| `additional_instructions` | string    | No       | Extra instructions for AI                          |

**Response:** `201 Created`

```json
{
  "id": 2,
  "name": "Kid-Friendly Italian Chicken Pasta",
  "description": "A delicious and easy pasta dish the whole family will love",
  "instructions": "Step 1: Cook pasta according to package...",
  "ingredients_text": ["500g chicken breast", "400g penne pasta", ...],
  "generated_by_llm": true,
  "nutrition_info": {"calories": 520, "protein_g": 35, ...},
  "match_score": 0.75,
  ...
}
```

**Error Response:** `503 Service Unavailable`

```json
{
  "error": "OpenRouter API key not configured"
}
```

---

### Fork a Recipe

Create a customized version of a recipe.

```
POST /recipes/{id}/fork/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "custom_ingredients": [
    "500g tofu (instead of chicken)",
    "2 cups mixed greens"
  ],
  "custom_instructions": "Use tofu instead of chicken, press and cube before grilling",
  "notes": "Made it vegan-friendly"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "original_recipe": 2,
  "original_recipe_name": "Grilled Chicken Salad",
  "custom_ingredients": [
    "500g tofu (instead of chicken)",
    "2 cups mixed greens"
  ],
  "custom_instructions": "Use tofu instead of chicken...",
  "notes": "Made it vegan-friendly",
  "created_at": "2026-02-16T12:00:00Z",
  "updated_at": "2026-02-16T12:00:00Z"
}
```

---

### List My Forked Recipes

```
GET /recipes/my-forks/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

---

## Analytics (Premium)

> ⚠️ These endpoints require a premium subscription.

### Nutrition Analytics

Get weekly macro statistics.

```
GET /analytics/nutrition/
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `days` | integer | Number of days to analyze (default: 7, max: 30) |

**Response:** `200 OK`

```json
{
  "period_days": 7,
  "recipe_count": 12,
  "total_nutrition": {
    "calories": 4200,
    "protein_g": 300,
    "carbs_g": 480,
    "fat_g": 144,
    "fiber_g": 60
  },
  "average_per_recipe": {
    "calories": 350,
    "protein_g": 25,
    "carbs_g": 40,
    "fat_g": 12,
    "fiber_g": 5
  },
  "daily_breakdown": {
    "2026-02-15": {
      "calories": 700,
      "protein_g": 50,
      "carbs_g": 80,
      "fat_g": 24,
      "fiber_g": 10,
      "recipe_count": 2
    }
  }
}
```

**Error Response:** `403 Forbidden`

```json
{
  "error": "Premium subscription required for analytics"
}
```

---

### Inventory Analytics

Get inventory statistics.

```
GET /analytics/inventory/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "total_items": 25,
  "perishable_items": 18,
  "expired_items": 2,
  "expiring_within_week": 5,
  "expiring_items": [
    { "id": 3, "name": "Milk", "quantity": "1L", "expiry_date": "2026-02-18" },
    {
      "id": 7,
      "name": "Yogurt",
      "quantity": "500g",
      "expiry_date": "2026-02-20"
    }
  ],
  "tag_distribution": [
    { "tags__name": "Protein", "count": 8 },
    { "tags__name": "Vegetable", "count": 6 },
    { "tags__name": "Dairy", "count": 4 }
  ]
}
```

---

## Subscription

### List Subscription Plans

```
GET /subscription/plans/
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Free",
    "features": ["Basic inventory", "5 AI recipes/month"],
    "price": "0.00",
    "description": "Get started for free",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Premium",
    "features": [
      "Unlimited inventory",
      "Unlimited AI recipes",
      "Nutrition analytics",
      "Priority support"
    ],
    "price": "9.99",
    "description": "Full access to all features",
    "is_active": true
  }
]
```

---

### Upgrade Subscription

```
POST /subscription/upgrade/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "plan_id": 2
}
```

**Response:** `200 OK`

```json
{
  "message": "Successfully upgraded to Premium",
  "subscription_type": "premium",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "subscription_type": "premium",
    "is_premium": true,
    ...
  }
}
```

---

## Community

### Browse Community Recipes

```
GET /community/recipes/
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tags` | integer[] | Filter by dietary tag IDs |
| `difficulty` | string | `easy`, `medium`, `hard` |
| `search` | string | Search by recipe name |
| `sort` | string | Sort field: `created_at`, `-created_at`, `name`, `-name`, `match_score`, `-match_score` |

**Example:** `GET /community/recipes/?difficulty=easy&search=chicken&sort=-created_at`

**Response:** `200 OK`

```json
{
  "count": 50,
  "results": [
    {
      "id": 10,
      "name": "Easy Lemon Chicken",
      "description": "Quick weeknight dinner",
      "tags": [{ "id": 1, "name": "Protein" }],
      "match_score": 0.0,
      "total_time_minutes": 30,
      "servings": 4,
      "difficulty": "easy",
      "is_public": true,
      "created_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

---

### Get Community Recipe Details

```
GET /community/recipes/{id}/
```

**Response:** `200 OK`

---

### Popular Recipes

Get most forked recipes.

```
GET /community/recipes/popular/
```

**Response:** `200 OK`

---

### Fork Community Recipe

```
POST /community/recipes/{id}/fork/
Authorization: Bearer <access_token>
```

**Response:** `201 Created`

```json
{
  "id": 5,
  "original_recipe": 10,
  "original_recipe_name": "Easy Lemon Chicken",
  "custom_ingredients": ["4 chicken thighs", "2 lemons", ...],
  "custom_instructions": "",
  "notes": "",
  "created_at": "2026-02-16T12:00:00Z",
  "updated_at": "2026-02-16T12:00:00Z"
}
```

---

## Error Responses

### Common Error Codes

| Code  | Description                              |
| ----- | ---------------------------------------- |
| `400` | Bad Request - Invalid input data         |
| `401` | Unauthorized - Missing or invalid token  |
| `403` | Forbidden - Insufficient permissions     |
| `404` | Not Found - Resource doesn't exist       |
| `503` | Service Unavailable - External API error |

### Error Format

```json
{
  "error": "Error message description"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message for this field"]
}
```

---

## Rate Limiting

- Standard users: 100 requests/minute
- Premium users: 500 requests/minute
- AI recipe generation: daily limits based on subscription (free=5, premium=50, pro=100)

---

## Health Profile Schema

The `health_profile` field accepts the following structure:

```json
{
  "allergies": ["peanuts", "shellfish", "dairy"],
  "dietary_restrictions": [
    "vegetarian",
    "vegan",
    "gluten-free",
    "keto",
    "paleo"
  ],
  "health_goals": ["weight_loss", "muscle_gain", "maintenance", "heart_health"],
  "preferred_cuisines": ["italian", "asian", "mexican", "mediterranean"],
  "disliked_ingredients": ["cilantro", "olives"],
  "calorie_target": 2000
}
```

All fields are optional.

---

## Rewards and History

### Get Base Profile

```
GET /users/profile/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "height_cm": 170,
  "weight_kg": "68.00",
  "allergies": ["peanuts"],
  "dietary_restrictions": ["vegetarian"],
  "fitness_goals": ["weight_loss"],
  "budget_limit": "2000.00",
  "calorie_target": 2000,
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:00:00Z"
}
```

### Update Base Profile

```
PATCH /users/profile/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "height_cm": 172,
  "allergies": ["peanuts", "shellfish"],
  "calorie_target": 2100
}
```

### Get Rewards

```
GET /users/rewards/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "points": 120,
  "streak_count": 7,
  "last_cooked_date": "2026-02-16",
  "badges": ["Budget Boss", "Green Chef", "Waste Warrior"],
  "updated_at": "2026-02-16T10:05:00Z"
}
```

### List Meal History

```
GET /recipes/history/
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "recipe": 5,
      "recipe_name": "Spinach Egg Scramble",
      "cooked_at": "2026-02-16T10:10:00Z",
      "rating": 5,
      "notes": "Quick and tasty",
      "used_inventory_only": true,
      "savings_estimate": "25.00"
    }
  ]
}
```

### Log a Meal

```
POST /recipes/<id>/log-meal/
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "rating": 5,
  "notes": "Quick and tasty",
  "used_inventory_only": true,
  "savings_estimate": "25.00"
}
```
