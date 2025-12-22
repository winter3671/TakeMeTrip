<template>
  <div class="kakao-login-btn" @click="loginWithKakao">
    <img
      src="https://k.kakaocdn.net/14/dn/btroDszwNrM/I6efHub1SN5KCJqLm1Ovx1/o.jpg"
      width="222"
      alt="카카오 로그인 버튼"
    />
  </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  if (window.Kakao && !window.Kakao.isInitialized()) {
    window.Kakao.init(import.meta.env.VITE_KAKAO_JS_KEY) 
    console.log('Kakao Init:', window.Kakao.isInitialized())
  }
})

const loginWithKakao = () => {
  window.Kakao.Auth.login({
    success: (authObj) => {
      console.log('카카오 토큰:', authObj)
      sendTokenToBackend(authObj.access_token)
    },
    fail: (err) => {
      console.error('로그인 실패:', err)
    },
  })
}

const sendTokenToBackend = async (accessToken) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/users/kakao/login/', {
      access_token: accessToken,
    })

    console.log('로그인 성공:', response.data)
    
    localStorage.setItem('accessToken', response.data.key || response.data.access)
    
    alert('환영합니다!')
    router.push('/')

  } catch (error) {
    console.error('서버 로그인 에러:', error)
    alert('로그인에 실패했습니다.')
  }
}
</script>

<style scoped>
.kakao-login-btn {
  cursor: pointer;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>