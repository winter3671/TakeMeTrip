from django.urls import path
from .views import AIPlannerView, CourseSaveView

urlpatterns = [
    path('generate/', AIPlannerView.as_view(), name='ai-planner-generate'),
    path('save/', CourseSaveView.as_view(), name='course-save'),
]