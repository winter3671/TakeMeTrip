from django.urls import path
from .views import AIPlannerView, CourseSaveView, get_region_list

urlpatterns = [
    path('generate/', AIPlannerView.as_view(), name='ai-planner-generate'),
    path('save/', CourseSaveView.as_view(), name='course-save'),
    path('locations/', get_region_list, name='region-list'),    
]