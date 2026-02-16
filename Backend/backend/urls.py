"""
URL configuration for backend project.

NourishNest API v1 routes:
- /api/v1/auth/ - Authentication endpoints
- /api/v1/users/ - User profile endpoints
- /api/v1/inventory/ - Inventory CRUD
- /api/v1/recipes/ - Recipe CRUD and generation
- /api/v1/analytics/ - Nutrition analytics (premium)
- /api/v1/subscription/ - Subscription plans
- /api/v1/community/ - Community recipe browsing
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 endpoints
    path('api/v1/', include('users.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/recipes/', include('recipes.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/community/', include('community.urls')),
    path('api/v1/paypal/', include('paypal_integration.urls')),
]
