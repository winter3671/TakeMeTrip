from rest_framework import serializers
from .models import Trip, TripImage, Category

class TripImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripImage
        fields = ['image_url', 'order']
        
class TripListSerializer(serializers.ModelSerializer):
    region_name = serializers.ReadOnlyField(source='region.name')
    city_name = serializers.ReadOnlyField(source='city.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 
            'title', 
            'thumbnail_image', 
            'region_name', 
            'city_name', 
            'category_name', 
            'recommendation_score',
            'mapx', 
            'mapy',
            'is_liked',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlists.filter(user=request.user).exists()
        return False

class TripDetailSerializer(serializers.ModelSerializer):
    region_name = serializers.ReadOnlyField(source='region.name')
    city_name = serializers.ReadOnlyField(source='city.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    images = TripImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = '__all__'

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlists.filter(user=request.user).exists()
        return False

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', ]