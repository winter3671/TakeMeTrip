from rest_framework import serializers
from .models import Course, CourseDetail
from trips.serializers import TripListSerializer
from trips.models import Region, City

class PlannerInputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    num_people = serializers.IntegerField(min_value=1)
    region_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    
    current_mapx = serializers.FloatField(required=True) # 현재 경도
    current_mapy = serializers.FloatField(required=True) # 현재 위도

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("종료일은 시작일보다 빠를 수 없습니다.")
        return data
    
class CourseDetailSerializer(serializers.ModelSerializer):
    trip = TripListSerializer(read_only=True)

    class Meta:
        model = CourseDetail
        fields = ['day', 'order', 'trip']

class CourseSerializer(serializers.ModelSerializer):
    details = CourseDetailSerializer(many=True, read_only=True) 

    class Meta:
        model = Course
        fields = ['id', 'title', 'region', 'start_date', 'end_date', 'created_at', 'details']
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class RegionSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)
    class Meta:
        model = Region
        fields = ['id', 'name', 'cities']
