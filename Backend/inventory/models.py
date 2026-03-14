from django.conf import settings
from django.db import models


class DietaryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('g', 'g'), ('kg', 'kg'), ('ml', 'ml'), ('L', 'L'),
        ('oz', 'oz'), ('lbs', 'lbs'), ('cups', 'cups'),
        ('tbsp', 'tbsp'), ('tsp', 'tsp'), ('pieces', 'pieces'),
        ('whole', 'whole'), ('slices', 'slices'), ('pinch', 'pinch'),
        ('bunch', 'bunch'), ('cans', 'cans'), ('boxes', 'boxes'),
        ('bags', 'bags'), ('jars', 'jars'), ('bottles', 'bottles'),
        ('cloves', 'cloves'), ('sprigs', 'sprigs'), ('leaves', 'leaves'),
        ('stalks', 'stalks'), ('heads', 'heads'), ('packages', 'packages')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='inventory_items')
    name = models.CharField(max_length=200)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    perishable = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(DietaryTag,blank=True,related_name='inventory_items')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['expiry_date', 'name']
        indexes = [models.Index(fields=['user', 'expiry_date']),models.Index(fields=['user', 'perishable']),]
    
    def __str__(self):
        return f"{self.name} ({self.quantity}) - {self.user.email}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class UserHistory(models.Model):
    class ActionType(models.TextChoices):
        ADD = 'add', 'Add'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        UNDO = 'undo', 'Undo'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='action_history')
    action_type = models.CharField(max_length=20,choices=ActionType.choices)
    model_affected = models.CharField(max_length=100,help_text="Name of the model that was affected")
    object_id = models.PositiveIntegerField(null=True,blank=True,help_text="ID of the affected object")
    metadata = models.JSONField(default=dict,help_text="Additional data for undo operations (old values, etc.)")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_undone = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'user histories'
        indexes = [models.Index(fields=['user', '-timestamp']),models.Index(fields=['user', 'is_undone']),]
    
    def __str__(self):
        return f"{self.user.email} - {self.action_type} {self.model_affected} at {self.timestamp}"
