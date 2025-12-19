from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .models import Trip, Wishlist
from .serializers import TripListSerializer, TripDetailSerializer
from django.db.models import Q

class TripListView(generics.ListAPIView):
    serializer_class = TripListSerializer

    def get_queryset(self):
        queryset = Trip.objects.filter(status='active')

        is_featured = self.request.query_params.get('featured', None)
        region_slug = self.request.query_params.get('region', None)
        search_keyword = self.request.query_params.get('search', None)
        sort_by = self.request.query_params.get('sort', None)

        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)

        if region_slug:
            queryset = queryset.filter(region__slug=region_slug)

        if search_keyword:
            queryset = queryset.filter(
                Q(title__contains=search_keyword) | 
                Q(description__contains=search_keyword) |
                Q(destination__contains=search_keyword)
            )

        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-recommendation_score')

        return queryset

class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.filter(status='active')
    serializer_class = TripDetailSerializer

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
        
class MyWishlistView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TripListSerializer

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(wishlists__user=user).order_by('-wishlists__created_at')