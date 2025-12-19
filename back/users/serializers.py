from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        data['phone'] = self.validated_data.get('phone', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get('name')
        user.phone = self.cleaned_data.get('phone')
        user.save()
        return user