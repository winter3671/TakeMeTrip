from django.urls import path
from .views import AIPlannerView

urlpatterns = [
    path('generate/', AIPlannerView.as_view(), name='ai-planner-generate'),
]