from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe


class IsPremiumUser:
    """Permission check for premium users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_premium


class NutritionAnalyticsView(APIView):
    """
    GET /api/v1/analytics/nutrition/
    Return weekly macro stats for premium users.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check premium subscription
        if not request.user.is_premium:
            return Response(
                {'error': 'Premium subscription required for analytics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get time range (default: last 7 days)
        days = int(request.query_params.get('days', 7))
        days = min(days, 30)  # Cap at 30 days
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get user's recipes from this period
        recipes = Recipe.objects.filter(
            created_by=request.user,
            created_at__gte=start_date
        )
        
        # Aggregate nutrition info
        total_nutrition = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
        }
        
        recipe_count = 0
        daily_breakdown = {}
        
        for recipe in recipes:
            nutrition = recipe.nutrition_info or {}
            if nutrition:
                recipe_count += 1
                for key in total_nutrition:
                    total_nutrition[key] += nutrition.get(key, 0)
                
                # Daily breakdown
                date_str = recipe.created_at.date().isoformat()
                if date_str not in daily_breakdown:
                    daily_breakdown[date_str] = {
                        'calories': 0,
                        'protein_g': 0,
                        'carbs_g': 0,
                        'fat_g': 0,
                        'fiber_g': 0,
                        'recipe_count': 0,
                    }
                
                for key in total_nutrition:
                    daily_breakdown[date_str][key] += nutrition.get(key, 0)
                daily_breakdown[date_str]['recipe_count'] += 1
        
        # Calculate averages
        avg_nutrition = {}
        if recipe_count > 0:
            for key, value in total_nutrition.items():
                avg_nutrition[key] = round(value / recipe_count, 1)
        
        return Response({
            'period_days': days,
            'recipe_count': recipe_count,
            'total_nutrition': total_nutrition,
            'average_per_recipe': avg_nutrition,
            'daily_breakdown': daily_breakdown,
        })


class InventoryAnalyticsView(APIView):
    """
    GET /api/v1/analytics/inventory/
    Return inventory stats (expiring items, usage patterns).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_premium:
            return Response(
                {'error': 'Premium subscription required for analytics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from inventory.models import InventoryItem
        
        today = timezone.now().date()
        week_ahead = today + timedelta(days=7)
        
        items = InventoryItem.objects.filter(user=request.user)
        
        # Count stats
        total_items = items.count()
        perishable_items = items.filter(perishable=True).count()
        expired_items = items.filter(expiry_date__lt=today).count()
        expiring_soon = items.filter(
            expiry_date__gte=today,
            expiry_date__lte=week_ahead
        ).count()
        
        # Items expiring soon (list)
        expiring_list = items.filter(
            expiry_date__gte=today,
            expiry_date__lte=week_ahead
        ).values('id', 'name', 'quantity', 'expiry_date')[:10]
        
        # Tag distribution
        from django.db.models import Count
        tag_stats = items.values('tags__name').annotate(
            count=Count('id')
        ).filter(tags__name__isnull=False).order_by('-count')[:10]
        
        return Response({
            'total_items': total_items,
            'perishable_items': perishable_items,
            'expired_items': expired_items,
            'expiring_within_week': expiring_soon,
            'expiring_items': list(expiring_list),
            'tag_distribution': list(tag_stats),
        })
