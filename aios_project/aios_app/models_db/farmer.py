from django.db import models
from .user import User
from django.core.exceptions import ValidationError

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone = models.CharField(max_length=20, blank=True)
    fullnames = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    farm_size_ha = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    preferred_language = models.CharField(max_length=10, blank=True)  # e.g., 'rw', 'en', 'sw'
    extra = models.JSONField(default=dict, blank=True)  # flexible add-ons
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='Active')

    def clean(self):
        role = str(getattr(self.user, 'role', '')).lower()
        if role and role != 'farmer':
            raise ValidationError({'user': 'Selected user does not have role=farmer'})

    def save(self, *args, **kwargs):
        self.full_clean()  # enforces role check
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Farmer: {self.user.username if self.user_id else 'Unknown'}"