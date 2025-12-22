from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User

class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    
    def save(self, request):
        user = super().save(request)
        return user