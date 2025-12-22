from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # 이미 연결된 소셜 계정이면 패스
        if sociallogin.is_existing:
            return

        # 소셜 계정에서 이메일 가져오기
        user = sociallogin.user
        if not user.email:
            return

        # 같은 이메일을 가진 기존 유저 찾기
        User = get_user_model()
        
        existing_user = User.objects.filter(email=user.email).first()
        
        if existing_user:
            # 기존 유저가 있다면 연결
            sociallogin.connect(request, existing_user)