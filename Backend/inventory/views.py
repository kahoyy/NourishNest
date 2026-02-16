from django.db import transaction
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DietaryTag, InventoryItem, UserHistory
from .serializers import (
    DietaryTagSerializer,
    InventoryItemSerializer,
    InventoryItemCreateSerializer,
    UserHistorySerializer,
)


class DietaryTagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/inventory/tags/ - List all dietary tags
    GET /api/v1/inventory/tags/<id>/ - Get tag details
    """
    queryset = DietaryTag.objects.all()
    serializer_class = DietaryTagSerializer
    permission_classes = [IsAuthenticated]


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for inventory items.
    
    GET /api/v1/inventory/ - List user's items
    POST /api/v1/inventory/ - Add new item
    GET /api/v1/inventory/<id>/ - Get item details
    PATCH /api/v1/inventory/<id>/ - Update item
    DELETE /api/v1/inventory/<id>/ - Remove item
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = InventoryItem.objects.filter(user=self.request.user)
        
        # Filter by perishable
        perishable = self.request.query_params.get('perishable')
        if perishable is not None:
            queryset = queryset.filter(perishable=perishable.lower() == 'true')
        
        # Filter by tags
        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        
        # Filter expired items
        expired = self.request.query_params.get('expired')
        if expired is not None:
            from django.utils import timezone
            today = timezone.now().date()
            if expired.lower() == 'true':
                queryset = queryset.filter(expiry_date__lt=today)
            else:
                queryset = queryset.filter(expiry_date__gte=today) | queryset.filter(expiry_date__isnull=True)
        
        return queryset.select_related('user').prefetch_related('tags')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InventoryItemCreateSerializer
        return InventoryItemSerializer
    
    def perform_create(self, serializer):
        item = serializer.save()
        # Record in history
        self._record_history('add', item)
    
    def perform_update(self, serializer):
        # Store old values for undo
        old_data = InventoryItemSerializer(serializer.instance).data
        item = serializer.save()
        self._record_history('update', item, old_data=old_data)
    
    def perform_destroy(self, instance):
        # Store full data for undo
        old_data = InventoryItemSerializer(instance).data
        old_data['tag_ids'] = list(instance.tags.values_list('id', flat=True))
        item_id = instance.id
        instance.delete()
        self._record_history('delete', None, object_id=item_id, old_data=old_data)
    
    def _record_history(self, action_type, item=None, object_id=None, old_data=None):
        """Record action in UserHistory for undo support."""
        UserHistory.objects.create(
            user=self.request.user,
            action_type=action_type,
            model_affected='InventoryItem',
            object_id=item.id if item else object_id,
            metadata={
                'old_data': old_data or {},
                'action': action_type,
            }
        )


class UndoView(APIView):
    """
    POST /api/v1/inventory/undo/
    Undo the last inventory action (LIFO stack).
    """
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        # Get the last undoable action
        last_action = UserHistory.objects.filter(
            user=request.user,
            model_affected='InventoryItem',
            is_undone=False
        ).exclude(action_type='undo').first()
        
        if not last_action:
            return Response(
                {'error': 'No actions to undo'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        old_data = last_action.metadata.get('old_data', {})
        
        try:
            if last_action.action_type == 'add':
                # Undo add: delete the item
                item = InventoryItem.objects.get(id=last_action.object_id)
                item.delete()
                result = {'message': f'Deleted item: {item.name}'}
                
            elif last_action.action_type == 'delete':
                # Undo delete: recreate the item
                tag_ids = old_data.pop('tag_ids', [])
                old_data.pop('id', None)
                old_data.pop('is_expired', None)
                old_data.pop('created_at', None)
                old_data.pop('updated_at', None)
                old_data.pop('tags', None)
                old_data['user'] = request.user
                
                item = InventoryItem.objects.create(**old_data)
                if tag_ids:
                    item.tags.set(tag_ids)
                result = {
                    'message': f'Restored item: {item.name}',
                    'item': InventoryItemSerializer(item).data
                }
                
            elif last_action.action_type == 'update':
                # Undo update: restore old values
                item = InventoryItem.objects.get(id=last_action.object_id)
                tag_ids = old_data.pop('tag_ids', None)
                
                for field in ['name', 'quantity', 'perishable', 'expiry_date', 'notes']:
                    if field in old_data:
                        setattr(item, field, old_data[field])
                
                item.save()
                if tag_ids:
                    item.tags.set(tag_ids)
                    
                result = {
                    'message': f'Restored item to previous state: {item.name}',
                    'item': InventoryItemSerializer(item).data
                }
            else:
                return Response(
                    {'error': 'Unknown action type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark action as undone
            last_action.is_undone = True
            last_action.save()
            
            # Record the undo action
            UserHistory.objects.create(
                user=request.user,
                action_type='undo',
                model_affected='InventoryItem',
                object_id=last_action.object_id,
                metadata={'undone_action_id': last_action.id}
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except InventoryItem.DoesNotExist:
            return Response(
                {'error': 'Item no longer exists'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserHistoryListView(generics.ListAPIView):
    """
    GET /api/v1/inventory/history/
    List user's action history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    
    def get_queryset(self):
        return UserHistory.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')[:50]
