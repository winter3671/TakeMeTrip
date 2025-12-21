from django.db import models
from users.models import User
from django.conf import settings

class Region(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'regions'

class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    external_code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cities'

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon_url = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'

class Trip(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    
    external_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    destination = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.IntegerField(default=1)
    thumbnail_image = models.CharField(max_length=500, blank=True)
    
    status = models.CharField(max_length=20, default='active')
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    
    is_ai_recommended = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    recommendation_score = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_trips')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    mapx = models.FloatField(default=0.0) # 경도
    mapy = models.FloatField(default=0.0) # 위도

    class Meta:
        db_table = 'trips'

class TripImage(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trip_images'
        ordering = ['order']

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    tag_type = models.CharField(max_length=20)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'

class TripTag(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trip_tags'
        unique_together = ['trip', 'tag']

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists'
        unique_together = ('user', 'trip')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.trip.title}"
    
# 사용자별 코스 저장
class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=100, default="나만의 여행 코스")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'

    def __str__(self):
        return f"[{self.user.email}] {self.title}"

# 코스에 포함된 여행지 
class CoursePlace(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='places')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    # 날짜 선택 기능(추후 추가 예정으로, 지금은 1로 설정)
    day = models.PositiveIntegerField(default=1)
    
    # 방문 순서
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_places'
        # DB에서 가져올 때 '날짜 순' -> '순서 순'으로 자동 정렬
        ordering = ['day', 'order']

    def __str__(self):
        return f"{self.course.title} ({self.day}일차 - {self.order}번째): {self.trip.title}"