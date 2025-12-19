from django.urls import path
from .views import TripListView, TripDetailView, TripLikeView, MyWishlistView

urlpatterns = [
    path('', TripListView.as_view(), name='trip_list'),
    path('<int:pk>/', TripDetailView.as_view(), name='trip_detail'),
    path('<int:pk>/like/', TripLikeView.as_view(), name='trip-like'),
    path('my/wishlist/', MyWishlistView.as_view(), name='my-wishlist'),
]