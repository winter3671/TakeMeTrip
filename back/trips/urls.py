from django.urls import path
from .views import TripListView, TripDetailView
from . import views

urlpatterns = [
    path('', TripListView.as_view(), name='trip_list'),
    path('<int:pk>/', TripDetailView.as_view(), name='trip_detail'),
    path('categories/', views.category_list, name='category-list'),
]