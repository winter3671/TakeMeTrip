<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h2 class="login-title">Login</h2>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <input type="text" id="username" v-model.trim="username" placeholder="USERNAME">
        </div>

        <div class="input-group">
          <input type="password" id="password" v-model.trim="password" placeholder="PASSWORD">
        </div>

        <button type="submit" class="login-btn">LOGIN</button>

        <div class="links">
          <a href="#" class="link-text">Forgot Password?</a>
          <RouterLink class="link-text signup" :to="{ name : 'signup'}">회원가입</RouterLink>
        </div>
      </form>

      <div class="social-login">
        
        <button class="social-btn google" @click="loginWithGoogle">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="social-icon-svg">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
              <path fill="none" d="M0 0h48v48H0z"></path>
            </svg>
          </div>
          <span class="btn-text">Google로 시작하기</span>
        </button>

        <button type="button" class="social-btn kakao" @click="kakaoLogin">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="social-icon-svg">
              <path fill="#3C1E1E" d="M12 3C5.9 3 1 6.9 1 11.8c0 3.2 2.1 6 5.4 7.6-.2.8-.8 2.8-.9 3.2 0 .3.2.5.4.5.1 0 .2 0 .3-.1 2.9-2 4.2-3.2 4.3-3.2 0 0 .2 0 .3 0 .5 0 1 0 1.5-.1 6.1 0 11-3.9 11-8.7C23 6.9 18.1 3 12 3z"/>
            </svg>
          </div>
          <span class="btn-text">카카오로 시작하기</span>
        </button>

        <button class="social-btn naver" @click="loginWithNaver">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="social-icon-svg">
              <path fill="#FFFFFF" d="M4 20V4h5.4l6.8 10V4h5.4v16h-5.4l-6.8-10v10H4z"/>
            </svg>
          </div>
          <span class="btn-text">네이버로 시작하기</span>
        </button>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute, RouterLink } from 'vue-router';
import axios from 'axios';
import { useTripStore } from '@/stores/trips';
import { useAccountStore } from '@/stores/accounts';

const tripStore = useTripStore();
const accountStore = useAccountStore(); 
const router = useRouter();
const route = useRoute();

const username = ref('');
const password = ref('');

const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_JS_KEY
const REST_API_KEY = import.meta.env.VITE_REST_API_KEY
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_CLIENT_ID

const CALLBACK_URI = 'http://localhost:5173/auth/callback';

const handleLogin = async function () {
  if (!username.value || !password.value) {
    alert('아이디와 비밀번호를 모두 입력해주세요.');
    return;
  }

  const payload = {
    username: username.value,
    password: password.value
  };

  try {
    await accountStore.logIn(payload);
  } catch (error) {
    console.error('로그인 에러:', error);

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      if (status === 400) {
        if (data.non_field_errors) {
           alert('아이디 또는 비밀번호가 올바르지 않습니다.');
        } else {
           alert('로그인 정보를 다시 확인해주세요.');
        }
      } else {
        alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    } else {
      alert('네트워크 오류가 발생했습니다.');
    }
  }
};

onMounted(async () => {
  if (window.Kakao && !window.Kakao.isInitialized()) {
    window.Kakao.init(KAKAO_JS_KEY);
  }
  if (route.query.code) {
    await getKakaoToken(route.query.code);
  }
});

const kakaoLogin = () => {
  window.Kakao.Auth.authorize({
    redirectUri: 'http://localhost:5173/login', 
  });
};

const getKakaoToken = async (code) => {
  try {
    const data = new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: REST_API_KEY,
      redirect_uri: 'http://localhost:5173/login',
      code: code,
    });

    const response = await axios.post(
      'https://kauth.kakao.com/oauth/token',
      data,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        },
      }
    );

    const accessToken = response.data.access_token;
    await sendTokenToBackend(accessToken);

  } catch (error) {
    console.error('토큰 교환 실패:', error);
    alert('카카오 로그인 중 오류가 발생했습니다.');
  }
};

const sendTokenToBackend = async (accessToken) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/social/kakao/login/', {
      access_token: accessToken,
    });

    localStorage.setItem('accessToken', response.data.key || response.data.access);
    
    accountStore.token = response.data.key || response.data.access;

    router.replace('/'); 

  } catch (error) {
    console.error('백엔드 로그인 에러:', error);
    alert('서버 로그인 실패');
  }
};
  const loginWithNaver = () => {
      const state = Math.random().toString(36).substring(7);
      const url = `https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=${NAVER_CLIENT_ID}&state=${state}&redirect_uri=${CALLBACK_URI}`;
      window.location.href = url;
  };

  const loginWithGoogle = () => {
      const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${CALLBACK_URI}&response_type=code&scope=email profile`;
      window.location.href = url;
  };
</script>

<style scoped>
.login-wrapper { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 80vh; 
  background-color: #fff; 
}

.login-container { 
  width: 100%; 
  max-width: 400px; 
  padding: 40px; 
  text-align: center; 
}

.login-title { 
  font-size: 32px; 
  font-weight: 700; 
  color: #333; 
  margin-bottom: 50px; 
}

.input-group { 
  margin-bottom: 30px; 
  text-align: left; 
}

.input-group label { 
  display: block; 
  font-size: 12px; 
  font-weight: 600; 
  color: #666; 
  margin-bottom: 8px; 
}

.input-group input { 
  width: 100%; 
  padding: 10px 0; 
  border: none; 
  border-bottom: 1px solid #ccc; 
  font-size: 16px; 
  outline: none; 
  transition: border-color 0.3s; 
}

.input-group input:focus { 
  border-bottom-color: #333; 
}

.login-btn { 
  width: 100%; 
  padding: 15px 0; 
  background-color: #1e6bba; 
  color: white; 
  border: none; 
  border-radius: 25px; 
  font-size: 16px; 
  font-weight: 700; 
  cursor: pointer; 
  margin-top: 10px; 
  margin-bottom: 20px; 
}

.links { 
  display: flex; 
  justify-content: center; 
  gap: 20px; 
  font-size: 14px; 
}

.link-text { 
  text-decoration: none; 
  color: #7d7dff; 
}

.social-login { 
  margin-top: 50px; 
  display: flex; 
  flex-direction: column; 
  gap: 12px; 
}

.social-btn { 
  width: 100%; 
  height: 50px; 
  border-radius: 6px; 
  border: none; 
  cursor: pointer; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  font-size: 15px; 
  font-weight: 600; 
  position: relative; 
  transition: opacity 0.2s; 
}

.social-btn:hover { 
  opacity: 0.9; 
}

.icon-wrapper { 
  position: absolute; 
  left: 20px; 
  width: 24px; 
  height: 24px; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
}

.social-icon-svg { 
  width: 100%; 
  height: 100%; 
}

.google { 
  background-color: #ffffff; 
  border: 1px solid #ddd; 
  color: #333; 
}

.kakao { 
  background-color: #FEE500; 
  color: #3C1E1E; 
}

.naver { 
  background-color: #03C75A; 
  color: #ffffff; 
}
</style>