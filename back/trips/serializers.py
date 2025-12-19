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
        ]

class TripDetailSerializer(serializers.ModelSerializer):
    region_name = serializers.ReadOnlyField(source='region.name')
    city_name = serializers.ReadOnlyField(source='city.name')
    category_name = serializers.ReadOnlyField(source='category.name')
    images = TripImageSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', ]