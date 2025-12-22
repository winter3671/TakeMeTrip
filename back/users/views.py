from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class CustomOAuth2Client(OAuth2Client):
    def __init__(self, request, consumer_key, consumer_secret, access_token_method, access_token_url, callback_url, scope=None, scope_delimiter=' ', headers=None, basic_auth=False):
        super().__init__(
            request, 
            consumer_key, 
            consumer_secret, 
            access_token_method, 
            access_token_url, 
            callback_url, 
            scope_delimiter, 
            headers, 
            basic_auth
        )

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomOAuth2Client
    callback_url = "http://localhost:5173/auth/callback"

class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter

class NaverLogin(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    client_class = CustomOAuth2Client
    callback_url = "http://localhost:5173/auth/callback"