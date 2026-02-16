from rest_framework import serializers

from .models import DietaryTag, InventoryItem, UserHistory


class DietaryTagSerializer(serializers.ModelSerializer):
    """Serializer for dietary tags."""
    
    class Meta:
        model = DietaryTag
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for inventory items."""
    
    tags = DietaryTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DietaryTag.objects.all(),
        write_only=True,
        required=False,
        source='tags'
    )
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'quantity', 'perishable', 'expiry_date',
            'tags', 'tag_ids', 'notes', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_expired', 'created_at', 'updated_at']
    
    def validate_expiry_date(self, value):
        """Warn if expiry date is in the past."""
        from django.utils import timezone
        if value and value < timezone.now().date():
            # Allow past dates but could add warning header
            pass
        return value


class InventoryItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating inventory items with auto-tag assignment."""
    
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DietaryTag.objects.all(),
        required=False,
        source='tags'
    )
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'quantity', 'perishable', 'expiry_date',
            'tag_ids', 'notes'
        ]
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['user'] = self.context['request'].user
        item = InventoryItem.objects.create(**validated_data)
        if tags:
            item.tags.set(tags)
        return item


class UserHistorySerializer(serializers.ModelSerializer):
    """Serializer for user action history."""
    
    class Meta:
        model = UserHistory
        fields = [
            'id', 'action_type', 'model_affected', 'object_id',
            'metadata', 'timestamp', 'is_undone'
        ]
        read_only_fields = ['id', 'timestamp']
