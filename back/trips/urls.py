from django.urls import path
from .views import TripListView, TripDetailView, TripLikeView, MyWishlistView, RandomTripView
from . import views

urlpatterns = [
    path('', TripListView.as_view(), name='trip_list'),
    path('<int:pk>/', TripDetailView.as_view(), name='trip_detail'),
    path('<int:pk>/like/', TripLikeView.as_view(), name='trip-like'),
    path('my/wishlist/', MyWishlistView.as_view(), name='my-wishlist'),
    path('categories/', views.category_list, name='category-list'),
    path('random/', RandomTripView.as_view(), name='trip-random'),
]