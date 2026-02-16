from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, UserForkedRecipesView, MealHistoryListView

router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('my-forks/', UserForkedRecipesView.as_view(), name='user-forks'),
    path('history/', MealHistoryListView.as_view(), name='meal-history'),
    path('', include(router.urls)),
]
