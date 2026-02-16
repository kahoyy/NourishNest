from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SubscriptionPlan, UserBaseProfile, UserRewards
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    UserBaseProfileSerializer,
    SubscriptionPlanSerializer,
    UpgradeSubscriptionSerializer,
    UserRewardsSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Register a new user account.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        UserBaseProfile.objects.get_or_create(user=user)
        UserRewards.objects.get_or_create(user=user)
        
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/users/me/ - Get current user profile
    PATCH /api/v1/users/me/ - Update profile info
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserProfileUpdateSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user


class SubscriptionPlanListView(generics.ListAPIView):
    """
    GET /api/v1/subscription/plans/
    List available subscription plans.
    """
    permission_classes = [AllowAny]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class UpgradeSubscriptionView(APIView):
    """
    POST /api/v1/subscription/upgrade/
    Upgrade user's subscription plan.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = UpgradeSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Map plan name to subscription type
        plan_type_mapping = {
            'free': User.SubscriptionType.FREE,
            'premium': User.SubscriptionType.PREMIUM,
            'pro': User.SubscriptionType.PRO,
        }
        
        new_type = plan_type_mapping.get(
            plan.name.lower(),
            User.SubscriptionType.PREMIUM
        )
        
        # Update user subscription
        request.user.subscription_type = new_type
        request.user.save(update_fields=['subscription_type'])
        
        return Response({
            'message': f'Successfully upgraded to {plan.name}',
            'subscription_type': request.user.subscription_type,
            'user': UserSerializer(request.user).data
        })


class UserBaseProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/users/profile/
    PATCH /api/v1/users/profile/
    Manage structured base profile data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserBaseProfileSerializer

    def get_object(self):
        profile, _ = UserBaseProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserRewardsView(generics.RetrieveAPIView):
    """
    GET /api/v1/users/rewards/
    Retrieve current rewards and streaks.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRewardsSerializer

    def get_object(self):
        rewards, _ = UserRewards.objects.get_or_create(user=self.request.user)
        return rewards
