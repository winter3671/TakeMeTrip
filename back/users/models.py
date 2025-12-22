from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    user_type = models.CharField(max_length=20, default='user')
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
    )
    
    class Meta:
        db_table = 'users'

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    favorite_regions = models.TextField(blank=True)
    budget_min = models.IntegerField(null=True, blank=True)
    budget_max = models.IntegerField(null=True, blank=True)
    travel_styles = models.TextField(blank=True)
    preferred_season = models.CharField(max_length=20, blank=True)
    usual_duration = models.IntegerField(null=True, blank=True)
    usual_people = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'