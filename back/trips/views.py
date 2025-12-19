from django.shortcuts import render
from rest_framework import generics
from .models import Trip
from .serializers import TripListSerializer, TripDetailSerializer

class TripListView(generics.ListAPIView):
    queryset = Trip.objects.filter(status='active').order_by('-recommendation_score')
    serializer_class = TripListSerializer

class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.filter(status='active')
    serializer_class = TripDetailSerializer