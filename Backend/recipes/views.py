from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F, Q, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from inventory.models import DietaryTag, InventoryItem
from users.services import process_meal_rewards
from .models import Recipe, RecipeFork, MealHistory, RecipeGenerationUsage, RecipeReview
from .serializers import (RecipeSerializer,RecipeListSerializer,RecipeGenerateSerializer,RecipeForkSerializer,RecipeForkCreateSerializer,MealHistorySerializer,MealHistoryCreateSerializer,RecipeReviewSerializer)
from .services import (generate_recipe_sync,calculate_match_score,get_banned_tags,apply_safe_filter,get_merged_health_profile,fork_recipe,)

DAILY_GENERATION_LIMITS = getattr(settings, 'DAILY_GENERATION_LIMITS', {'free': 5,'premium': 50,'pro': 100,})
DEFAULT_DAILY_LIMIT = 5
FAR_FUTURE_DAYS = 3650


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.filter(Q(created_by=user) | Q(is_public=True)).annotate(
            fork_count=Count('forks', distinct=True),
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews', distinct=True)
        ).distinct()

        min_score = self.request.query_params.get('min_score')
        if min_score:
            try:
                queryset = queryset.filter(match_score__gte=float(min_score))
            except ValueError:
                pass

        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()

        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        ai_generated = self.request.query_params.get('ai_generated')
        if ai_generated is not None:
            queryset = queryset.filter(generated_by_llm=ai_generated.lower() == 'true')

        queryset = apply_safe_filter(queryset, user)
        return queryset.prefetch_related('tags')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = RecipeGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        rate_error = self._enforce_rate_limit(request.user)
        if rate_error:
            return rate_error

        inventory_data = self._gather_inventory(request.user, data)
        if not inventory_data:
            return Response({'error': 'No inventory items available for recipe generation'},status=status.HTTP_400_BAD_REQUEST,)

        health_profile = get_merged_health_profile(request.user)
        options = {
            'cuisine_preference': data.get('cuisine_preference', ''),
            'max_prep_time': data.get('max_prep_time'),
            'servings': data.get('servings', 2),
            'additional_instructions': data.get('additional_instructions', ''),
            'strict_inventory_only': data.get('strict_inventory_only', False),
        }

        result = generate_recipe_sync(inventory_data, health_profile, options)
        if 'error' in result:
            return Response({'error': result['error']},status=status.HTTP_503_SERVICE_UNAVAILABLE,)

        tags_data = result.pop('tags', [])
        banned = {tag.lower() for tag in get_banned_tags(request.user)}
        if banned:
            for tag_name in tags_data:
                if str(tag_name).lower() in banned:
                    return Response({'error': 'Generated recipe conflicts with dietary restrictions'},status=status.HTTP_400_BAD_REQUEST,)
        match_score = calculate_match_score(result.get('ingredients_text', []), inventory_data)
        recipe = self._create_recipe(result, request.user, match_score, tags_data)

        return Response(RecipeSerializer(recipe).data,status=status.HTTP_201_CREATED,)

    @action(detail=False, methods=['get'])
    def generation_usage(self, request):
        today = timezone.now().date()
        daily_limit = DAILY_GENERATION_LIMITS.get(
            request.user.subscription_type, DEFAULT_DAILY_LIMIT
        )
        usage = RecipeGenerationUsage.objects.filter(
            user=request.user, date=today
        ).first()
        used = usage.count if usage else 0
        return Response({
            'used': used,
            'limit': daily_limit,
            'remaining': max(daily_limit - used, 0),
            'subscription_type': request.user.subscription_type,
        })

    def _enforce_rate_limit(self, user):
        today = timezone.now().date()
        daily_limit = DAILY_GENERATION_LIMITS.get(user.subscription_type, DEFAULT_DAILY_LIMIT)

        usage, created = RecipeGenerationUsage.objects.get_or_create(user=user,date=today,defaults={'count': 0},)

        rows_updated = RecipeGenerationUsage.objects.filter(pk=usage.pk,count__lt=daily_limit,).update(count=F('count') + 1)

        if rows_updated == 0:
            return Response({'error': 'Daily AI generation limit reached'},status=status.HTTP_429_TOO_MANY_REQUESTS,)
        return None

    def _gather_inventory(self, user, data):
        if not data.get('use_inventory', True):
            return []

        if data.get('inventory_item_ids'):
            items = InventoryItem.objects.filter(user=user,id__in=data['inventory_item_ids'],)
        else:
            items = InventoryItem.objects.filter(user=user,).exclude(expiry_date__lt=timezone.now().date(),)

        items = list(items)
        far_future = timezone.now().date() + timedelta(days=FAR_FUTURE_DAYS)
        items.sort(key=lambda item: (not item.perishable,item.expiry_date is None,item.expiry_date or far_future,))

        quantity_overrides = data.get('inventory_item_quantities', {})
        return [
            {
                'name': item.name,
                'quantity': quantity_overrides.get(str(item.id), item.quantity),
            }
            for item in items
        ]

    def _create_recipe(self, result, user, match_score, tags_data):
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
            created_by=user,
            is_public=False,
        )

        for tag_name in tags_data:
            tag, _ = DietaryTag.objects.get_or_create(name__iexact=tag_name,defaults={'name': tag_name},)
            recipe.tags.add(tag)

        return recipe


    @action(detail=True, methods=['post'])
    def fork(self, request, pk=None):
        recipe = self.get_object()
        serializer = RecipeForkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        fork, created = fork_recipe(
            recipe,
            request.user,
            custom_ingredients=serializer.validated_data.get('custom_ingredients'),
            custom_instructions=serializer.validated_data.get('custom_instructions', ''),
            notes=serializer.validated_data.get('notes', ''),
        )

        if not created:
            return Response({'error': 'You have already forked this recipe','fork': RecipeForkSerializer(fork).data,},status=status.HTTP_400_BAD_REQUEST,)

        return Response(RecipeForkSerializer(fork).data,status=status.HTTP_201_CREATED,)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        recipe = self.get_object()
        
        if request.method == 'GET':
            reviews = recipe.reviews.all().select_related('user')
            serializer = RecipeReviewSerializer(reviews, many=True)
            return Response(serializer.data)
            
        if recipe.created_by == request.user:
            return Response({'error': 'You cannot review your own recipe'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RecipeReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if RecipeReview.objects.filter(recipe=recipe, user=request.user).exists():
            return Response({'error': 'You have already reviewed this recipe'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.save(recipe=recipe, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def log_meal(self, request, pk=None):
        recipe = self.get_object()
        serializer = MealHistoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        import re
        history = MealHistory.objects.create(user=request.user,recipe=recipe,**serializer.validated_data,)

        if history.used_inventory_only:
            inventory_items = list(InventoryItem.objects.filter(user=request.user))
            for ingredient in recipe.ingredients_text:
                ingredient_lower = ingredient.lower()
                for inv_item in inventory_items:
                    if inv_item.name.lower() in ingredient_lower:
                        match = re.match(r'^([\d\.]+)', ingredient.strip())
                        qty_to_reduce = 1.0
                        if match:
                            try:
                                qty_to_reduce = float(match.group(1))
                            except ValueError:
                                pass
                        
                        inv_item.quantity -= float(qty_to_reduce)
                        if inv_item.quantity <= 0:
                            inv_item.delete()
                            inventory_items.remove(inv_item)
                        else:
                            inv_item.save()
                        break

        from users.services import calculate_meal_points
        points_earned = calculate_meal_points(used_inventory_only=history.used_inventory_only,rating=history.rating,savings_estimate=history.savings_estimate,)
        process_meal_rewards(request.user,recipe,used_inventory_only=history.used_inventory_only,rating=history.rating,savings_estimate=history.savings_estimate,)

        data = MealHistorySerializer(history).data
        data['points_earned'] = points_earned
        return Response(data,status=status.HTTP_201_CREATED,)


class UserForkedRecipesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeForkSerializer

    def get_queryset(self):
        return RecipeFork.objects.filter(forked_by=self.request.user,).select_related('original_recipe')


class ForkDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeForkSerializer

    def get_queryset(self):
        return RecipeFork.objects.filter(forked_by=self.request.user).select_related('original_recipe')


class MealHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealHistorySerializer

    def get_queryset(self):
        return MealHistory.objects.filter(user=self.request.user).select_related('recipe')
