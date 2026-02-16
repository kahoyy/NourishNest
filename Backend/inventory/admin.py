from django.contrib import admin

from .models import DietaryTag, InventoryItem, UserHistory


@admin.register(DietaryTag)
class DietaryTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'quantity', 'perishable', 'expiry_date', 'created_at']
    list_filter = ['perishable', 'tags', 'created_at']
    search_fields = ['name', 'user__email']
    autocomplete_fields = ['user', 'tags']
    date_hierarchy = 'created_at'


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'model_affected', 'timestamp', 'is_undone']
    list_filter = ['action_type', 'model_affected', 'is_undone']
    search_fields = ['user__email']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action_type', 'model_affected', 'object_id', 'metadata', 'timestamp']
