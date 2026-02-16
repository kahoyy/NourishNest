from django.urls import path

from .views import NutritionAnalyticsView, InventoryAnalyticsView

urlpatterns = [
    path('nutrition/', NutritionAnalyticsView.as_view(), name='analytics-nutrition'),
    path('inventory/', InventoryAnalyticsView.as_view(), name='analytics-inventory'),
]
