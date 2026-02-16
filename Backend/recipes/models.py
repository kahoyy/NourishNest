from django.conf import settings
from django.db import models


class Recipe(models.Model):
    """Stores recipes, including AI-generated ones."""
    
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    instructions = models.TextField(
        help_text="Step-by-step cooking instructions"
    )
    ingredients = models.ManyToManyField(
        'inventory.InventoryItem',
        blank=True,
        related_name='used_in_recipes',
        help_text="Linked inventory items used in this recipe"
    )
    ingredients_text = models.JSONField(
        default=list,
        help_text="List of ingredient strings with quantities"
    )
    tags = models.ManyToManyField(
        'inventory.DietaryTag',
        blank=True,
        related_name='recipes'
    )
    generated_by_llm = models.BooleanField(
        default=False,
        help_text="Whether this recipe was AI-generated"
    )
    nutrition_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Nutritional information: calories, protein, carbs, fat, etc."
    )
    match_score = models.FloatField(
        default=0.0,
        help_text="Score indicating how well this matches user's inventory (0-1)"
    )
    prep_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    cook_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    servings = models.PositiveIntegerField(default=2)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='medium'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_recipes'
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this recipe is visible to the community"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_score', '-created_at']
        indexes = [
            models.Index(fields=['is_public', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['-match_score']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def total_time_minutes(self):
        prep = self.prep_time_minutes or 0
        cook = self.cook_time_minutes or 0
        return prep + cook


class RecipeFork(models.Model):
    """Tracks when users fork/customize existing recipes."""
    
    original_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='forks'
    )
    forked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forked_recipes'
    )
    custom_ingredients = models.JSONField(
        default=list,
        help_text="Modified ingredients list"
    )
    custom_instructions = models.TextField(
        blank=True,
        help_text="Custom modifications to the original instructions"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['original_recipe', 'forked_by']
    
    def __str__(self):
        return f"{self.forked_by.email}'s fork of {self.original_recipe.name}"


class MealHistory(models.Model):
    """Tracks cooked meals and feedback for adaptation and rewards."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_history'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='meal_history'
    )
    cooked_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    used_inventory_only = models.BooleanField(default=True)
    savings_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-cooked_at']
        indexes = [
            models.Index(fields=['user', '-cooked_at']),
        ]

    def __str__(self):
        return f"{self.user.email} cooked {self.recipe.name}"
