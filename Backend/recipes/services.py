"""
OpenRouter API service for recipe generation.
"""
import json
import logging

import httpx
from django.conf import settings
import paypalrestsdk

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = getattr(settings, 'OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = getattr(settings, 'OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')


def build_recipe_prompt(inventory_items: list, health_profile: dict, options: dict) -> str:
    """Build the prompt for recipe generation."""
    
    # Format inventory items
    ingredients_list = "\n".join([
        f"- {item['name']}: {item['quantity']}" 
        for item in inventory_items
    ])
    
    # Format health profile
    health_info = ""
    if health_profile:
        if health_profile.get('allergies'):
            health_info += f"\nAllergies to avoid (STRICT): {', '.join(health_profile['allergies'])}"
        if health_profile.get('dietary_restrictions'):
            health_info += f"\nDietary restrictions (STRICT): {', '.join(health_profile['dietary_restrictions'])}"
        if health_profile.get('health_goals'):
            health_info += f"\nHealth goals: {', '.join(health_profile['health_goals'])}"
        if health_profile.get('calorie_target'):
            health_info += f"\nTarget calories per serving: {health_profile['calorie_target']}"
    
    # Additional options
    cuisine = options.get('cuisine_preference', '')
    max_time = options.get('max_prep_time', '')
    servings = options.get('servings', 2)
    additional = options.get('additional_instructions', '')
    
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

Create a delicious, healthy recipe. You may suggest 1-2 additional common pantry items if needed.

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


async def generate_recipe_async(inventory_items: list, health_profile: dict, options: dict) -> dict:
    """
    Generate a recipe using OpenRouter API (async version).
    
    Args:
        inventory_items: List of inventory item dicts with 'name' and 'quantity'
        health_profile: User's health profile dict
        options: Additional options (cuisine_preference, max_prep_time, servings, etc.)
    
    Returns:
        Parsed recipe dict or error dict
    """
    if not OPENROUTER_API_KEY:
        return {
            'error': 'OpenRouter API key not configured',
            'fallback': True
        }
    
    prompt = build_recipe_prompt(inventory_items, health_profile, options)
    
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://nourishnest.app',
        'X-Title': 'NourishNest Recipe Generator',
    }
    
    payload = {
        'model': 'openai/gpt-4o-mini',  # Cost-effective default
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
        'temperature': 0.7,
        'max_tokens': 2000,
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f'{OPENROUTER_BASE_URL}/chat/completions',
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            recipe_data = json.loads(content.strip())
            recipe_data['generated_by_llm'] = True
            
            return recipe_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
        return {'error': f'API error: {e.response.status_code}'}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse recipe JSON: {e}")
        return {'error': 'Failed to parse recipe response'}
    except Exception as e:
        logger.error(f"Recipe generation error: {e}")
        return {'error': str(e)}


def generate_recipe_sync(inventory_items: list, health_profile: dict, options: dict) -> dict:
    """
    Generate a recipe using OpenRouter API (sync version).
    """
    if not OPENROUTER_API_KEY:
        return {
            'error': 'OpenRouter API key not configured',
            'fallback': True
        }
    
    prompt = build_recipe_prompt(inventory_items, health_profile, options)
    
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://nourishnest.app',
        'X-Title': 'NourishNest Recipe Generator',
    }
    
    payload = {
        'model': 'openai/gpt-4o-mini',
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
        'temperature': 0.7,
        'max_tokens': 2000,
    }
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f'{OPENROUTER_BASE_URL}/chat/completions',
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            recipe_data = json.loads(content.strip())
            recipe_data['generated_by_llm'] = True
            
            return recipe_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
        return {'error': f'API error: {e.response.status_code}'}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse recipe JSON: {e}")
        return {'error': 'Failed to parse recipe response'}
    except Exception as e:
        logger.error(f"Recipe generation error: {e}")
        return {'error': str(e)}


def calculate_match_score(recipe_ingredients: list, inventory_items: list) -> float:
    """
    Calculate how well a recipe matches available inventory.
    
    Returns a score from 0.0 to 1.0
    """
    if not recipe_ingredients or not inventory_items:
        return 0.0
    
    inventory_names = {item['name'].lower() for item in inventory_items}
    
    matched = 0
    for ingredient in recipe_ingredients:
        ingredient_lower = ingredient.lower()
        # Check if any inventory item name appears in the ingredient
        for inv_name in inventory_names:
            if inv_name in ingredient_lower or ingredient_lower in inv_name:
                matched += 1
                break
    
    return round(matched / len(recipe_ingredients), 2)


def create_payment(amount, currency="USD"):
    """
    Create a PayPal payment.
    :param amount: The amount to charge.
    :param currency: The currency for the payment.
    :return: The payment object.
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": f"{amount:.2f}",
                "currency": currency
            },
            "description": "Payment description"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/recipes/paypal/return",
            "cancel_url": "http://localhost:8000/recipes/paypal/cancel"
        }
    })

    if payment.create():
        return payment
    else:
        raise Exception(payment.error)


def execute_payment(payment_id, payer_id):
    """
    Execute a PayPal payment.
    :param payment_id: The ID of the payment to execute.
    :param payer_id: The ID of the payer.
    :return: The executed payment object.
    """
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return payment
    else:
        raise Exception(payment.error)
