from rest_framework import serializers
from .models import Trip, TripImage, Category, Course, CoursePlace

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

# 코스 내부의 각 여행지 정보
class CoursePlaceSerializer(serializers.ModelSerializer):
    trip = TripListSerializer(read_only=True)
    
    class Meta:
        model = CoursePlace
        fields = ['id', 'trip', 'order', 'day']

# 코스 전체 조회 및 생성/수정용
class CourseSerializer(serializers.ModelSerializer):
    places = CoursePlaceSerializer(many=True, read_only=True)
    
    place_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'places', 'place_ids', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    # [생성] POST /api/courses/
    def create(self, validated_data):
        place_ids = validated_data.pop('place_ids', [])
        user = validated_data.pop('user', self.context['request'].user)
        
        course = Course.objects.create(user=user, **validated_data)
        
        # day는 1로 고정
        for index, trip_id in enumerate(place_ids):
            if Trip.objects.filter(id=trip_id).exists():
                CoursePlace.objects.create(
                    course=course,
                    trip_id=trip_id,
                    order=index,
                    day=1
                )
        return course

    # [수정] PATCH /api/courses/{id}/
    def update(self, instance, validated_data):
        place_ids = validated_data.get('place_ids', None)
        
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # 여행지 리스트가 새로 왔을 때 전체를 지우고 새로 저장
        if place_ids is not None:
            instance.places.all().delete()
            
            for index, trip_id in enumerate(place_ids):
                if Trip.objects.filter(id=trip_id).exists():
                    CoursePlace.objects.create(
                        course=instance,
                        trip_id=trip_id,
                        order=index,
                        day=1
                    )
                    
        return instance