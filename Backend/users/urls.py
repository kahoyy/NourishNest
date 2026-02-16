from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    LogoutView,
    UserProfileView,
    UserBaseProfileView,
    UserRewardsView,
    SubscriptionPlanListView,
    UpgradeSubscriptionView,
)

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    
    # User endpoints
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/profile/', UserBaseProfileView.as_view(), name='user-base-profile'),
    path('users/rewards/', UserRewardsView.as_view(), name='user-rewards'),
    
    # Subscription endpoints
    path('subscription/plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscription/upgrade/', UpgradeSubscriptionView.as_view(), name='subscription-upgrade'),
]
