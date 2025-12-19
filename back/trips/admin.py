from django.contrib import admin
from .models import Trip, TripImage, Region, City, Category, Tag, TripTag

class TripImageInline(admin.TabularInline):
    model = TripImage
    extra = 1

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'region', 'city', 'mapx', 'mapy', 'recommendation_score'] # 목록에 표시할 항목
    search_fields = ['title', 'description'] # 검색 기능
    list_filter = ['region', 'category'] # 필터 기능
    inlines = [TripImageInline] # 이미지 추가 가능

admin.site.register(Region)
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(TripTag)