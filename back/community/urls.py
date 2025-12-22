from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:article_pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:article_pk>/comments/', views.comment_create, name='comment_create'),
    path('articles/<int:article_pk>/likes/', views.like_article, name='like_article'),
    path('articles/<int:article_pk>/comments/<int:comment_pk>/', views.comment_delete, name='comment_delete'),
]
