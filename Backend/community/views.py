from django.db.models import Count, Avg
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe, RecipeFork
from recipes.serializers import RecipeListSerializer, RecipeSerializer, RecipeForkSerializer
from recipes.services import apply_safe_filter, fork_recipe

POPULAR_RECIPES_LIMIT = 20
VALID_SORT_FIELDS = frozenset(['created_at', '-created_at','name', '-name','match_score', '-match_score',])


class CommunityRecipeListView(generics.ListAPIView):
    """
    GET /api/v1/community/recipes/
    Browse public/shared recipes from the community.
    """
    permission_classes = [AllowAny]
    serializer_class = RecipeListSerializer

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_public=True).annotate(
            fork_count=Count('forks', distinct=True),
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews', distinct=True)
        )

        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        sort = self.request.query_params.get('sort', '-created_at')
        if sort in VALID_SORT_FIELDS:
            queryset = queryset.order_by(sort)
        user = self.request.user
        if user.is_authenticated:
            queryset = apply_safe_filter(queryset, user)
        return queryset.prefetch_related('tags').select_related('created_by')


class CommunityRecipeDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.filter(is_public=True).annotate(
        fork_count=Count('forks', distinct=True),
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )


class CommunityRecipeForkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk, is_public=True)
        except Recipe.DoesNotExist:
            return Response({'error': 'Recipe not found or not public'},status=status.HTTP_404_NOT_FOUND,)

        fork, created = fork_recipe(recipe, request.user)

        if not created:
            return Response({'error': 'You have already forked this recipe','fork': RecipeForkSerializer(fork).data,},status=status.HTTP_400_BAD_REQUEST,)

        return Response(RecipeForkSerializer(fork).data,status=status.HTTP_201_CREATED,)


class PopularRecipesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecipeListSerializer

    def get_queryset(self):
        return (Recipe.objects.filter(is_public=True).annotate(fork_count=Count('forks')).order_by('-fork_count')[:POPULAR_RECIPES_LIMIT])
