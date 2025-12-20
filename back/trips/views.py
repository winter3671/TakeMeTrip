from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Trip, Wishlist, Category
from .serializers import TripListSerializer, TripDetailSerializer, CategorySerializer

# 1. 여행지 목록 조회 (필터링, 검색, 정렬 포함 - 최신 버전)
class TripListView(ListAPIView):
    serializer_class = TripListSerializer
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'overview', 'destination']
    ordering_fields = ['recommendation_score', 'created_at']

    def get_queryset(self):
        # 1. 기본 쿼리셋 (활성 상태인 것만)
        queryset = Trip.objects.filter(status='active')

        # 2. 파라미터 받기
        area_name = self.request.query_params.get('area', None)
        category_id = self.request.query_params.get('category', None)
        
        # 3. 지역(area) 필터링
        if area_name and area_name != '전체':
            queryset = queryset.filter(
                Q(destination__contains=area_name) | 
                Q(city__name__contains=area_name) |
                Q(region__name__contains=area_name)
            ).distinct()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 5. 정렬 처리 (기본값 설정)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-recommendation_score')

        return queryset

# 2. 여행지 상세 조회
class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.filter(status='active')
    serializer_class = TripDetailSerializer

# 3. 찜하기 (좋아요) 토글 기능
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

# 4. 내 찜 목록 보기 (마이페이지)
class MyWishlistView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TripListSerializer

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(wishlists__user=user).order_by('-wishlists__created_at')

# 5. 카테고리 목록 (동료 작업분 반영)
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)