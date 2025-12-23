from rest_framework import serializers
from .models import Trip, TripImage, Category
from planner.models import Course as PlannerCourse, CourseDetail

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
            'start_date',
            'end_date'
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
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'thumbnail_image', 
            'region_name', 'city_name', 'category_name', 
            'recommendation_score', 'mapx', 'mapy', 'is_liked',
            'images', 'tags',
            'overview', 'tel', 'homepage', 
            'parking', 'rest_date', 'use_time',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlists.filter(user=request.user).exists()
        return False
    
    def get_tags(self, obj):
        # trip.triptag_set.all()로 연결된 태그들을 모두 가져와서 이름만 리스트로 반환
        return [item.tag.name for item in obj.triptag_set.all()]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', ]

class PlannerCourseDetailSerializer(serializers.ModelSerializer):
    """planner의 CourseDetail - 여행지 정보"""
    trip = TripListSerializer(read_only=True)
    trip_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CourseDetail
        fields = ['id', 'trip', 'trip_id', 'day', 'order']

class PlannerCourseSerializer(serializers.ModelSerializer):
    """planner의 Course - 여행 코스"""
    details = PlannerCourseDetailSerializer(many=True, read_only=True)
    trip_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = PlannerCourse
        fields = ['id', 'title', 'region', 'start_date', 'end_date', 'created_at', 'details', 'trip_ids']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        trip_ids = validated_data.pop('trip_ids', [])
        user = self.context['request'].user
        
        course = PlannerCourse.objects.create(user=user, **validated_data)
        
        for index, trip_id in enumerate(trip_ids):
            if Trip.objects.filter(id=trip_id).exists():
                CourseDetail.objects.create(
                    course=course,
                    trip_id=trip_id,
                    day=1,
                    order=index
                )
        return course

    def update(self, instance, validated_data):
        trip_ids = validated_data.pop('trip_ids', None)
        
        instance.title = validated_data.get('title', instance.title)
        instance.region = validated_data.get('region', instance.region)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()

        if trip_ids is not None:
            instance.details.all().delete()
            
            for index, trip_id in enumerate(trip_ids):
                if Trip.objects.filter(id=trip_id).exists():
                    CourseDetail.objects.create(
                        course=instance,
                        trip_id=trip_id,
                        day=1,
                        order=index
                    )
        
        return instance