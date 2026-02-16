from rest_framework import serializers

from inventory.serializers import DietaryTagSerializer
from inventory.models import DietaryTag
from .models import Recipe, RecipeFork, MealHistory


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe details."""
    
    tags = DietaryTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DietaryTag.objects.all(),
        write_only=True,
        required=False,
        source='tags'
    )
    total_time_minutes = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'instructions',
            'ingredients_text', 'tags', 'tag_ids',
            'generated_by_llm', 'nutrition_info', 'match_score',
            'prep_time_minutes', 'cook_time_minutes', 'total_time_minutes',
            'servings', 'difficulty', 'is_public',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'generated_by_llm', 'match_score',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for recipe listings."""
    
    tags = DietaryTagSerializer(many=True, read_only=True)
    total_time_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'tags',
            'match_score', 'total_time_minutes',
            'servings', 'difficulty', 'is_public',
            'created_at'
        ]


class RecipeGenerateSerializer(serializers.Serializer):
    """Serializer for recipe generation request."""
    
    use_inventory = serializers.BooleanField(
        default=True,
        help_text="Use items from user's inventory"
    )
    inventory_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Specific inventory item IDs to use"
    )
    cuisine_preference = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )
    max_prep_time = serializers.IntegerField(
        required=False,
        min_value=5,
        max_value=480
    )
    servings = serializers.IntegerField(
        default=2,
        min_value=1,
        max_value=20
    )
    additional_instructions = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )


class RecipeForkSerializer(serializers.ModelSerializer):
    """Serializer for recipe forks."""
    
    original_recipe_name = serializers.CharField(
        source='original_recipe.name',
        read_only=True
    )
    
    class Meta:
        model = RecipeFork
        fields = [
            'id', 'original_recipe', 'original_recipe_name',
            'custom_ingredients', 'custom_instructions', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['forked_by'] = self.context['request'].user
        return super().create(validated_data)


class RecipeForkCreateSerializer(serializers.Serializer):
    """Serializer for creating a fork from a recipe."""
    
    custom_ingredients = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        default=list
    )
    custom_instructions = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True
    )
    notes = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )


class MealHistorySerializer(serializers.ModelSerializer):
    """Serializer for meal history entries."""

    recipe_name = serializers.CharField(source='recipe.name', read_only=True)

    class Meta:
        model = MealHistory
        fields = [
            'id', 'recipe', 'recipe_name', 'cooked_at',
            'rating', 'notes', 'used_inventory_only', 'savings_estimate'
        ]
        read_only_fields = ['id', 'cooked_at', 'recipe_name']


class MealHistoryCreateSerializer(serializers.Serializer):
    """Serializer for creating meal history entries."""

    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    used_inventory_only = serializers.BooleanField(default=True)
    savings_estimate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
