import json
import logging
from typing import Optional
import httpx
from django.conf import settings
from .models import RecipeFork

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = getattr(settings, 'OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

DEFAULT_MODEL = getattr(settings, 'OPENROUTER_DEFAULT_MODEL', 'openai/gpt-4o-mini')
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000
API_TIMEOUT_SECONDS = 60.0


def build_recipe_prompt(inventory_items: list, health_profile: dict, options: dict) -> str:

    ingredients_list = "\n".join(
        f"- {item['name']}: {item['quantity']}"
        for item in inventory_items
    )

    health_info = _format_health_profile(health_profile)
    cuisine = options.get('cuisine_preference', '')
    max_time = options.get('max_prep_time', '')
    servings = options.get('servings', 2)
    additional = options.get('additional_instructions', '')
    strict_only = options.get('strict_inventory_only', False)
    strict_instruction = "\n- STRICT INGREDIENT REQUIREMENT: You MUST ONLY use the ingredients provided in the AVAILABLE INGREDIENTS list. Do NOT suggest or include any outside ingredients whatsoever." if strict_only else "\nYou may suggest 1-2 additional common pantry items if needed."
    
    prompt = f"""You are a professional chef and nutritionist. Create a recipe using the following ingredients from the user's inventory.

AVAILABLE INGREDIENTS:
{ingredients_list}

USER HEALTH PROFILE:{health_info if health_info else ' None specified'}

REQUIREMENTS:
- Servings: {servings}
{f'- Cuisine preference: {cuisine}' if cuisine else ''}
{f'- Maximum preparation time: {max_time} minutes' if max_time else ''}
{f'- Additional requests: {additional}' if additional else ''}
- Do not include any ingredients or tags that conflict with allergies or dietary restrictions. If unsure, exclude the item.

Create a delicious, healthy recipe.{strict_instruction}

Respond with a JSON object in this exact format:
{{
    "name": "Recipe Name",
    "description": "Brief appetizing description",
    "ingredients_text": ["1 cup ingredient1", "2 tbsp ingredient2", ...],
    "instructions": "Step 1: ...\\nStep 2: ...\\n...",
    "prep_time_minutes": 15,
    "cook_time_minutes": 30,
    "servings": {servings},
    "difficulty": "easy|medium|hard",
    "nutrition_info": {{
        "calories": 350,
        "protein_g": 25,
        "carbs_g": 40,
        "fat_g": 12,
        "fiber_g": 5
    }},
    "tags": ["tag1", "tag2"]
}}

Respond ONLY with the JSON object, no additional text."""

    return prompt


def _format_health_profile(health_profile: dict) -> str:
    if not health_profile:
        return ""

    parts = []
    if health_profile.get('allergies'):
        parts.append(f"\nAllergies to avoid (STRICT): {', '.join(health_profile['allergies'])}")
    if health_profile.get('dietary_restrictions'):
        parts.append(f"\nDietary restrictions (STRICT): {', '.join(health_profile['dietary_restrictions'])}")
    if health_profile.get('health_goals'):
        parts.append(f"\nHealth goals: {', '.join(health_profile['health_goals'])}")
    if health_profile.get('calorie_target'):
        parts.append(f"\nTarget calories per serving: {health_profile['calorie_target']}")
    return "".join(parts)


def _build_api_payload(prompt: str, servings: int = 2) -> dict:
    return {
        'model': DEFAULT_MODEL,
        'messages': [
            {
                'role': 'system',
                'content': 'You are a professional chef and nutritionist. Always respond with valid JSON only.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': DEFAULT_TEMPERATURE,
        'max_tokens': DEFAULT_MAX_TOKENS,
    }


def _get_api_headers() -> dict:
    """Build HTTP headers for OpenRouter API requests."""
    return {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://nourishnest.app',
        'X-Title': 'NourishNest Recipe Generator',
    }


def _parse_recipe_response(content: str) -> dict:
    """
    Parse the AI response into a recipe dictionary.
    Handles markdown code block wrappers.
    """
    cleaned = content.strip()

    if cleaned.startswith('```'):
        parts = cleaned.split('```')
        if len(parts) >= 2:
            cleaned = parts[1]
            if cleaned.startswith('json'):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    recipe_data = json.loads(cleaned)
    recipe_data['generated_by_llm'] = True
    return recipe_data


def _call_openrouter_api(payload: dict) -> str:
    headers = _get_api_headers()
    with httpx.Client(timeout=API_TIMEOUT_SECONDS) as client:
        response = client.post(f'{OPENROUTER_BASE_URL}/chat/completions',headers=headers,json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']


def generate_recipe_sync(inventory_items: list, health_profile: dict, options: dict) -> dict:

    if not OPENROUTER_API_KEY:
        return {'error': 'OpenRouter API key not configured', 'fallback': True}

    prompt = build_recipe_prompt(inventory_items, health_profile, options)
    payload = _build_api_payload(prompt)

    try:
        content = _call_openrouter_api(payload)
        return _parse_recipe_response(content)

    except httpx.HTTPStatusError as e:
        logger.error("OpenRouter API error: %s - %s", e.response.status_code, e.response.text)
        return {'error': f'API error: {e.response.status_code}'}
    except json.JSONDecodeError as e:
        logger.error("Failed to parse recipe JSON: %s", e)
        return {'error': 'Failed to parse recipe response'}
    except Exception as e:
        logger.error("Recipe generation error: %s", e)
        return {'error': 'Recipe generation failed. Please try again.'}


def fork_recipe(recipe, user, *, custom_ingredients=None, custom_instructions='', notes=''):
    existing = RecipeFork.objects.filter(original_recipe=recipe, forked_by=user).first()
    if existing:
        return existing, False
    if custom_ingredients is None:
        custom_ingredients = list(recipe.ingredients_text)
    fork = RecipeFork.objects.create(original_recipe=recipe, forked_by=user,custom_ingredients=custom_ingredients,custom_instructions=custom_instructions, notes=notes)
    return fork, True


def get_banned_tags(user):
    base = getattr(user, 'base_profile', None)
    if not base:
        return set()
    banned = list(base.allergies or [])
    return {str(t).strip() for t in banned if str(t).strip()}


def apply_safe_filter(queryset, user):
    if not user.is_authenticated:
        return queryset
    banned = get_banned_tags(user)
    if banned:
        queryset = queryset.exclude(tags__name__in=banned)
    return queryset


def get_merged_health_profile(user):
    base = getattr(user, 'base_profile', None)
    if not base:
        return {}
    return {'allergies': list(base.allergies or []),'dietary_restrictions': list(base.dietary_restrictions or []),'health_goals': list(base.fitness_goals or []),'calorie_target': base.calorie_target}


def calculate_match_score(recipe_ingredients: list, inventory_items: list) -> float:
    if not recipe_ingredients or not inventory_items:
        return 0.0

    inventory_names = {item['name'].lower() for item in inventory_items}

    matched = 0
    for ingredient in recipe_ingredients:
        ingredient_lower = ingredient.lower()
        for inv_name in inventory_names:
            if inv_name in ingredient_lower or ingredient_lower in inv_name:
                matched += 1
                break

    return round(matched / len(recipe_ingredients), 2)
