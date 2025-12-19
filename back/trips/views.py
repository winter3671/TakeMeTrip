from django.shortcuts import render
from rest_framework import generics
from .models import Trip
from .serializers import TripListSerializer, TripDetailSerializer

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