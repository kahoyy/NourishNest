from django.contrib import admin

from .models import Recipe, RecipeFork


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'difficulty', 'match_score', 'generated_by_llm', 'is_public', 'created_at']
    list_filter = ['difficulty', 'generated_by_llm', 'is_public', 'tags']
    search_fields = ['name', 'description', 'created_by__email']
    autocomplete_fields = ['created_by', 'tags']
    date_hierarchy = 'created_at'
    readonly_fields = ['match_score', 'created_at', 'updated_at']


@admin.register(RecipeFork)
class RecipeForkAdmin(admin.ModelAdmin):
    list_display = ['original_recipe', 'forked_by', 'created_at']
    search_fields = ['original_recipe__name', 'forked_by__email']
    autocomplete_fields = ['original_recipe', 'forked_by']
    date_hierarchy = 'created_at'
