from django.urls import path

from .views import (
    CommunityRecipeListView,
    CommunityRecipeDetailView,
    CommunityRecipeForkView,
    PopularRecipesView,
)

urlpatterns = [
    path('recipes/', CommunityRecipeListView.as_view(), name='community-recipes'),
    path('recipes/popular/', PopularRecipesView.as_view(), name='community-popular'),
    path('recipes/<int:pk>/', CommunityRecipeDetailView.as_view(), name='community-recipe-detail'),
    path('recipes/<int:pk>/fork/', CommunityRecipeForkView.as_view(), name='community-recipe-fork'),
]
