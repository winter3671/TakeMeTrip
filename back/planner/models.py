from django.db import models
from django.conf import settings

class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='planner_courses')
    title = models.CharField(max_length=100)
    region = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CourseDetail(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='details')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE)
    day = models.IntegerField()
    order = models.IntegerField()
    
    # 선택 사항: AI가 정해준 시간이나 메모를 저장하고 싶다면 필드 추가 가능
    # visit_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['day', 'order']