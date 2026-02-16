from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, SubscriptionPlan


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'subscription_type', 'is_staff', 'date_joined']
    list_filter = ['subscription_type', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('NourishNest', {'fields': ('subscription_type', 'health_profile')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('NourishNest', {'fields': ('email', 'subscription_type')}),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
