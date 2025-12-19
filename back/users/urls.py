from django.urls import path
from .views import GoogleLogin, KakaoLogin, NaverLogin

urlpatterns = [
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('kakao/', KakaoLogin.as_view(), name='kakao_login'),
    path('naver/', NaverLogin.as_view(), name='naver_login'),
]