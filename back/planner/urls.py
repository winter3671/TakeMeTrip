from django.urls import path
from .views import AIPlannerView, get_region_list

urlpatterns = [
    path('generate/', AIPlannerView.as_view(), name='ai-planner-generate'),
    path('locations/', get_region_list, name='region-list'),
]