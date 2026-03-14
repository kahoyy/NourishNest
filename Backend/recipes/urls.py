from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, UserForkedRecipesView, ForkDetailView, MealHistoryListView

router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('generation-usage/', RecipeViewSet.as_view({'get': 'generation_usage'})),
    path('my-forks/<int:pk>/', ForkDetailView.as_view(), name='fork-detail'),
    path('my-forks/', UserForkedRecipesView.as_view(), name='user-forks'),
    path('history/', MealHistoryListView.as_view(), name='meal-history'),
    path('', include(router.urls)),
]
