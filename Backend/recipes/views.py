from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventory.models import DietaryTag, InventoryItem
from users.models import RecipeGenerationUsage, UserRewards
from .models import Recipe, RecipeFork, MealHistory
from .serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    RecipeGenerateSerializer,
    RecipeForkSerializer,
    RecipeForkCreateSerializer,
    MealHistorySerializer,
    MealHistoryCreateSerializer,
)
from .services import generate_recipe_sync, calculate_match_score


class RecipeViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for recipes.
    
    GET /api/v1/recipes/ - List recipes
    POST /api/v1/recipes/ - Create recipe manually
    GET /api/v1/recipes/<id>/ - Get recipe details
    PATCH /api/v1/recipes/<id>/ - Update recipe
    DELETE /api/v1/recipes/<id>/ - Delete recipe
    POST /api/v1/recipes/generate/ - Generate recipe with AI
    POST /api/v1/recipes/<id>/fork/ - Fork a recipe
    """
    permission_classes = [IsAuthenticated]

    def _get_banned_tags(self, user):
        health_profile = user.health_profile or {}
        banned = []
        for key in ['allergies', 'dietary_restrictions']:
            values = health_profile.get(key, [])
            if isinstance(values, list):
                banned.extend(values)
        base_profile = getattr(user, 'base_profile', None)
        if base_profile:
            banned.extend(base_profile.allergies or [])
            banned.extend(base_profile.dietary_restrictions or [])
        return {str(tag).strip() for tag in banned if str(tag).strip()}

    def _apply_safe_filter(self, queryset, user):
        if not user.is_authenticated:
            return queryset
        banned = self._get_banned_tags(user)
        if banned:
            queryset = queryset.exclude(tags__name__in=banned)
        return queryset

    def _get_health_profile(self, user):
        profile = dict(user.health_profile or {})
        base_profile = getattr(user, 'base_profile', None)
        if base_profile:
            if base_profile.allergies:
                profile.setdefault('allergies', [])
                profile['allergies'] = list(set(profile['allergies']) | set(base_profile.allergies))
            if base_profile.dietary_restrictions:
                profile.setdefault('dietary_restrictions', [])
                profile['dietary_restrictions'] = list(
                    set(profile['dietary_restrictions']) | set(base_profile.dietary_restrictions)
                )
            if base_profile.fitness_goals:
                profile.setdefault('health_goals', [])
                profile['health_goals'] = list(set(profile['health_goals']) | set(base_profile.fitness_goals))
            if base_profile.calorie_target and not profile.get('calorie_target'):
                profile['calorie_target'] = base_profile.calorie_target
        return profile
    
    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.filter(
            # User's own recipes or public recipes
            created_by=user
        ) | Recipe.objects.filter(is_public=True)
        
        queryset = queryset.distinct()
        
        # Filter by match_score
        min_score = self.request.query_params.get('min_score')
        if min_score:
            try:
                queryset = queryset.filter(match_score__gte=float(min_score))
            except ValueError:
                pass
        
        # Filter by dietary tags
        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by generated_by_llm
        ai_generated = self.request.query_params.get('ai_generated')
        if ai_generated is not None:
            queryset = queryset.filter(generated_by_llm=ai_generated.lower() == 'true')
        
        queryset = self._apply_safe_filter(queryset, user)
        return queryset.prefetch_related('tags')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        POST /api/v1/recipes/generate/
        Generate a recipe using AI based on user's inventory and preferences.
        """
        serializer = RecipeGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Rate limiting (token bucket style)
        today = timezone.now().date()
        limit_map = {
            'free': 5,
            'premium': 50,
            'pro': 100,
        }
        daily_limit = limit_map.get(request.user.subscription_type, 5)
        usage, _ = RecipeGenerationUsage.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'count': 0}
        )
        if usage.count >= daily_limit:
            return Response(
                {'error': 'Daily AI generation limit reached'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        usage.count += 1
        usage.save(update_fields=['count'])

        # Get inventory items
        if data.get('use_inventory', True):
            if data.get('inventory_item_ids'):
                items = InventoryItem.objects.filter(
                    user=request.user,
                    id__in=data['inventory_item_ids']
                )
            else:
                # Get all non-expired items
                items = InventoryItem.objects.filter(
                    user=request.user
                ).exclude(
                    expiry_date__lt=timezone.now().date()
                )

            items = list(items)
            far_future = timezone.now().date() + timedelta(days=3650)
            items.sort(
                key=lambda item: (
                    not item.perishable,
                    item.expiry_date is None,
                    item.expiry_date or far_future
                )
            )
            inventory_data = [
                {'name': item.name, 'quantity': item.quantity}
                for item in items
            ]
        else:
            inventory_data = []
        
        if not inventory_data:
            return Response(
                {'error': 'No inventory items available for recipe generation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user health profile
        health_profile = self._get_health_profile(request.user)
        
        # Options for generation
        options = {
            'cuisine_preference': data.get('cuisine_preference', ''),
            'max_prep_time': data.get('max_prep_time'),
            'servings': data.get('servings', 2),
            'additional_instructions': data.get('additional_instructions', ''),
        }
        
        # Generate recipe
        result = generate_recipe_sync(inventory_data, health_profile, options)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Calculate match score
        match_score = calculate_match_score(
            result.get('ingredients_text', []),
            inventory_data
        )
        
        # Create recipe in database
        tags_data = result.pop('tags', [])

        # Reject recipes that conflict with allergies or restrictions
        banned = {tag.lower() for tag in self._get_banned_tags(request.user)}
        if banned:
            for tag_name in tags_data:
                if str(tag_name).lower() in banned:
                    return Response(
                        {'error': 'Generated recipe conflicts with dietary restrictions'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        recipe = Recipe.objects.create(
            name=result.get('name', 'AI Generated Recipe'),
            description=result.get('description', ''),
            instructions=result.get('instructions', ''),
            ingredients_text=result.get('ingredients_text', []),
            generated_by_llm=True,
            nutrition_info=result.get('nutrition_info', {}),
            match_score=match_score,
            prep_time_minutes=result.get('prep_time_minutes'),
            cook_time_minutes=result.get('cook_time_minutes'),
            servings=result.get('servings', 2),
            difficulty=result.get('difficulty', 'medium'),
            created_by=request.user,
            is_public=False,
        )
        
        # Add tags
        if tags_data:
            for tag_name in tags_data:
                tag, _ = DietaryTag.objects.get_or_create(
                    name__iexact=tag_name,
                    defaults={'name': tag_name}
                )
                recipe.tags.add(tag)
        
        return Response(
            RecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def fork(self, request, pk=None):
        """
        POST /api/v1/recipes/<id>/fork/
        Fork/customize an existing recipe.
        """
        recipe = self.get_object()
        
        # Check if user already forked this recipe
        existing_fork = RecipeFork.objects.filter(
            original_recipe=recipe,
            forked_by=request.user
        ).first()
        
        if existing_fork:
            return Response(
                {'error': 'You have already forked this recipe',
                 'fork': RecipeForkSerializer(existing_fork).data},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RecipeForkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        fork = RecipeFork.objects.create(
            original_recipe=recipe,
            forked_by=request.user,
            custom_ingredients=serializer.validated_data.get('custom_ingredients', []),
            custom_instructions=serializer.validated_data.get('custom_instructions', ''),
            notes=serializer.validated_data.get('notes', ''),
        )
        
        return Response(
            RecipeForkSerializer(fork).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def log_meal(self, request, pk=None):
        """
        POST /api/v1/recipes/<id>/log-meal/
        Log a cooked meal and update rewards.
        """
        recipe = self.get_object()
        serializer = MealHistoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        history = MealHistory.objects.create(
            user=request.user,
            recipe=recipe,
            **serializer.validated_data
        )

        rewards, _ = UserRewards.objects.get_or_create(user=request.user)
        today = timezone.now().date()
        points_to_add = 10 if history.used_inventory_only else 5
        if history.rating and history.rating >= 4:
            points_to_add += 5
        if history.savings_estimate and history.savings_estimate >= 20:
            points_to_add += 5
        rewards.points += points_to_add

        if rewards.last_cooked_date == today - timedelta(days=1):
            rewards.streak_count += 1
        elif rewards.last_cooked_date != today:
            rewards.streak_count = 1
        rewards.last_cooked_date = today

        badges = set(rewards.badges or [])
        if rewards.streak_count >= 7:
            badges.add('Waste Warrior')
        if rewards.points >= 100 or (history.savings_estimate and history.savings_estimate >= 50):
            badges.add('Budget Boss')
        if history.used_inventory_only and rewards.streak_count >= 3:
            badges.add('Green Chef')

        protein_g = None
        if recipe.nutrition_info:
            protein_g = recipe.nutrition_info.get('protein_g')
        if protein_g and protein_g >= 25:
            badges.add('Protein Pro')
        if recipe.tags.filter(name__iexact='protein').exists():
            badges.add('Protein Pro')

        rewards.badges = sorted(badges)
        rewards.save(update_fields=['points', 'streak_count', 'last_cooked_date', 'badges', 'updated_at'])

        return Response(
            MealHistorySerializer(history).data,
            status=status.HTTP_201_CREATED
        )


class UserForkedRecipesView(generics.ListAPIView):
    """
    GET /api/v1/recipes/my-forks/
    List user's forked recipes.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeForkSerializer
    
    def get_queryset(self):
        return RecipeFork.objects.filter(
            forked_by=self.request.user
        ).select_related('original_recipe')


class MealHistoryListView(generics.ListAPIView):
    """
    GET /api/v1/recipes/history/
    List user's meal history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MealHistorySerializer

    def get_queryset(self):
        return MealHistory.objects.filter(user=self.request.user).select_related('recipe')
