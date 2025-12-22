from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.db.models import Q, F, FloatField, ExpressionWrapper
from django_filters.rest_framework import DjangoFilterBackend

from .models import Trip, Wishlist, Category, Course, CoursePlace
from .serializers import TripListSerializer, TripDetailSerializer, CategorySerializer, CourseSerializer

# 여행지 목록 조회 (필터링, 검색, 정렬 포함)
class TripListView(ListAPIView):
    serializer_class = TripListSerializer
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'overview', 'destination']
    ordering_fields = ['recommendation_score', 'created_at']

    def get_queryset(self):
        queryset = Trip.objects.filter(status='active')

        area_name = self.request.query_params.get('area', None)
        category_id = self.request.query_params.get('category', None)
        ordering_param = self.request.query_params.get('ordering', None)

        lat = self.request.query_params.get('lat', None)
        lon = self.request.query_params.get('lon', None)
        
        if area_name and area_name != '전체':
            queryset = queryset.filter(
                Q(destination__contains=area_name) | 
                Q(city__name__contains=area_name) |
                Q(region__name__contains=area_name)
            ).distinct()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if ordering_param == 'distance' and lat and lon:
            try:
                current_lat = float(lat)
                current_lon = float(lon)

                queryset = queryset.annotate(
                    distance_diff=ExpressionWrapper(
                        (F('mapy') - current_lat) ** 2 + (F('mapx') - current_lon) ** 2,
                        output_field=FloatField()
                    )
                ).order_by('distance_diff')
            except ValueError:
                queryset = queryset.order_by('-created_at')

        elif ordering_param:
            queryset = queryset.order_by(ordering_param)
        else:
            queryset = queryset.order_by('-recommendation_score')

        return queryset

# 여행지 상세 조회
class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.filter(status='active')
    serializer_class = TripDetailSerializer

# 찜하기 (좋아요) 토글 기능
class TripLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def post(self, request, pk):
        trip = get_object_or_404(Trip, pk=pk)
        user = request.user

        wishlist, created = Wishlist.objects.get_or_create(user=user, trip=trip)

        if not created:
            wishlist.delete()
            return Response({'status': 'unliked', 'is_liked': False}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'liked', 'is_liked': True}, status=status.HTTP_201_CREATED)

# 내 찜 목록 보기 
class MyWishlistView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TripListSerializer

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(wishlists__user=user).order_by('-wishlists__created_at')

# 카테고리 목록 
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# 카테고리별 랜덤 추천 API
class RandomTripView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category')

        try:
            count = int(request.query_params.get('count', 4))
        except ValueError:
            count = 4
        
        queryset = Trip.objects.filter(status='active')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        random_trips = queryset.order_by('?')[:count]
        
        serializer = TripListSerializer(random_trips, many=True, context={'request': request})
        return Response(serializer.data)

# 코스 생성 및 내 코스 목록 조회
class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 코스 상세 조회, 순서변경, 삭제
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

# 내 위치 중심 주변 여행지 추천
class NearbyTripView(generics.ListAPIView):
    serializer_class = TripListSerializer
    pagination_class = None 

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        trip_id = self.request.query_params.get('trip_id')
        
        exclude_id = self.request.query_params.get('exclude_id')

        if trip_id:
            try:
                base_trip = Trip.objects.get(id=trip_id)
                lat = base_trip.mapy
                lon = base_trip.mapx
                exclude_id = base_trip.id # 자동으로 자기 자신 제외
            except Trip.DoesNotExist:
                return Trip.objects.none()

        if not lat or not lon:
            return Trip.objects.none()
            
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return Trip.objects.none()

        queryset = Trip.objects.filter(status='active')

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        # 거리 계산 및 정렬
        queryset = queryset.annotate(
            distance_diff=ExpressionWrapper(
                (F('mapy') - lat) ** 2 + (F('mapx') - lon) ** 2,
                output_field=FloatField()
            )
        ).order_by('distance_diff')

        return queryset[:10]
    
class BannerRandomView(APIView):
    def get(self, request):
        # 1. status가 active이고, 썸네일이 null이 아니며 빈 문자열도 아닌 데이터 필터링
        queryset = Trip.objects.filter(
            status='active',
            thumbnail_image__isnull=False
        ).exclude(thumbnail_image='')

        # 2. 전체 데이터 중에서 무작위로 섞은 뒤 10개만 슬라이싱
        random_trips = queryset.order_by('?')[:10]

        # 3. 직렬화 후 반환
        serializer = TripListSerializer(random_trips, many=True, context={'request': request})
        return Response(serializer.data)