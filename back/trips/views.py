from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, FloatField, ExpressionWrapper, Count
from django_filters.rest_framework import DjangoFilterBackend
from collections import Counter
import random

from .models import Trip, Wishlist, Category
from .serializers import TripListSerializer, TripDetailSerializer, CategorySerializer, PlannerCourseSerializer
from planner.models import Course as PlannerCourse, CourseDetail

class TripPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'  
    max_page_size = 150 

# 여행지 목록 조회 (필터링, 검색, 정렬 포함)
class TripListView(ListAPIView):
    serializer_class = TripListSerializer
    pagination_class = TripPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'overview', 'destination']
    ordering_fields = ['recommendation_score', 'created_at']

    def get_queryset(self):
        queryset = Trip.objects.filter(status='active')
        queryset = queryset.annotate(total_likes=Count('wishlists'))

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
                queryset = queryset.order_by('-total_likes', '-recommendation_score')

        elif ordering_param:
            queryset = queryset.order_by(ordering_param)
        else:
            # 1순위: 좋아요순, 2순위: 추천점수순, 3순위: 그래도 같으면 랜덤
            queryset = queryset.order_by('-total_likes', '-recommendation_score', '?')

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

    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(wishlists__user=user, status='active').order_by('-wishlists__created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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
    serializer_class = PlannerCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlannerCourse.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 코스 상세 조회, 순서변경, 삭제
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlannerCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlannerCourse.objects.filter(user=self.request.user)

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
                exclude_id = base_trip.id
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

        queryset = queryset.annotate(
            distance_diff=ExpressionWrapper(
                (F('mapy') - lat) ** 2 + (F('mapx') - lon) ** 2,
                output_field=FloatField()
            )
        ).order_by('distance_diff')

        return queryset[:10]
    
class BannerRandomView(APIView):
    def get(self, request):
        queryset = Trip.objects.filter(
            status='active',
            thumbnail_image__isnull=False
        ).exclude(thumbnail_image='')

        random_trips = queryset.order_by('?')[:10]

        serializer = TripListSerializer(random_trips, many=True, context={'request': request})
        return Response(serializer.data)

# 카테고리 별 추천
@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_by_category(request):
    category_code = request.GET.get('category')
    
    if not category_code:
        return Response({'message': '카테고리를 선택해주세요.'}, status=400)

    trips = Trip.objects.filter(category_id=category_code).order_by('?')[:10]
    
    serializer = TripListSerializer(trips, many=True, context={'request': request})
    return Response(serializer.data)

# 2. 내가 찜한 장소 (단순 랜덤)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_liked_places(request):
    user = request.user
    liked_trips = Trip.objects.filter(wishlists__user=user, status='active').order_by('?')[:10]
    
    serializer = TripListSerializer(liked_trips, many=True, context={'request': request})
    return Response(serializer.data)

# 3. AI 추천 장소 (가중치 알고리즘)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_by_ai(request):
    user = request.user
    city_id = request.query_params.get('city_id')
    category_name = request.query_params.get('category_name') # 추가
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    count = int(request.query_params.get('count', 10))
    
    my_wishlists = Wishlist.objects.filter(user=user).select_related('trip', 'trip__city', 'trip__category')
    my_liked_trip_ids = set(my_wishlists.values_list('trip_id', flat=True))

    liked_city_ids = []
    liked_category_ids = []
    if my_wishlists.exists():
        for w in my_wishlists:
            if w.trip.city_id: liked_city_ids.append(w.trip.city_id)
            if w.trip.category_id: liked_category_ids.append(w.trip.category_id)

    city_counter = Counter(liked_city_ids)
    category_counter = Counter(liked_category_ids)

    # 협업 필터링 (가중치 낮게 유지)
    similar_user_ids = Wishlist.objects.filter(trip_id__in=my_liked_trip_ids).exclude(user=user).values_list('user_id', flat=True)
    collab_counter = Counter(Wishlist.objects.filter(user_id__in=similar_user_ids).exclude(trip_id__in=my_liked_trip_ids).values_list('trip_id', flat=True))

    candidates = Trip.objects.filter(status='active').exclude(id__in=my_liked_trip_ids)
    
    # 사용자 요구사항: 지역 고정
    if city_id:
        candidates = candidates.filter(city_id=city_id)
    
    # 카테고리 필터 (숙소 등)
    if category_name:
        candidates = candidates.filter(category__name__contains=category_name)

    scored_trips = []
    
    target_lat = float(lat) if lat else None
    target_lng = float(lng) if lng else None

    for trip in candidates:
        score = 0
        if trip.category_id in category_counter:
            score += category_counter[trip.category_id] * 200
        if trip.city_id in city_counter:
            score += city_counter[trip.city_id] * 100
        if trip.id in collab_counter:
            score += collab_counter[trip.id] * 10
            
        score += trip.recommendation_score
        
        # 사용자 요구사항: 근접 장소 우선 추천
        if target_lat and target_lng and trip.mapy and trip.mapx:
            dist_sq = (trip.mapy - target_lat)**2 + (trip.mapx - target_lng)**2
            # 거리가 가까울수록 가점 (단위가 크므로 적절히 조정)
            if dist_sq < 0.01: # 약 1km 반경 근처 (매우 대략적)
                score += 500
            elif dist_sq < 0.04: # 약 2km 반경
                score += 200

        if score > 30:
            scored_trips.append((score, trip))

    scored_trips.sort(key=lambda x: x[0], reverse=True)
    
    # 상위 후보군 중 랜덤하게 섞어서 다양성 확보 (리롤 대응)
    pool_size = min(len(scored_trips), count * 3)
    top_candidates = [t for s, t in scored_trips[:pool_size]]
    
    final_trips = random.sample(top_candidates, min(len(top_candidates), count))

    serializer = TripListSerializer(final_trips, many=True, context={'request': request})
    return Response(serializer.data)
