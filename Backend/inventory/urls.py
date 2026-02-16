from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DietaryTagViewSet,
    InventoryItemViewSet,
    UndoView,
    UserHistoryListView,
)

router = DefaultRouter()
router.register(r'tags', DietaryTagViewSet, basename='dietary-tag')
router.register(r'', InventoryItemViewSet, basename='inventory-item')

urlpatterns = [
    path('undo/', UndoView.as_view(), name='inventory-undo'),
    path('history/', UserHistoryListView.as_view(), name='inventory-history'),
    path('', include(router.urls)),
]
