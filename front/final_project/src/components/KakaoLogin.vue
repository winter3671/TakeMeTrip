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

// 1. 카카오 SDK 초기화
onMounted(() => {
  if (window.Kakao && !window.Kakao.isInitialized()) {
    // ⚠️ 여기에 본인의 JavaScript 키를 넣으세요!
    window.Kakao.init('dc32b2b8795a175bdf7de2093e10fa6e') 
    console.log('Kakao Init:', window.Kakao.isInitialized())
  }
})

const loginWithKakao = () => {
  // 2. 카카오 로그인 창 띄우기
  window.Kakao.Auth.login({
    success: (authObj) => {
      console.log('카카오 토큰:', authObj)
      // 3. 백엔드로 토큰 전송
      sendTokenToBackend(authObj.access_token)
    },
    fail: (err) => {
      console.error('로그인 실패:', err)
    },
  })
}

const sendTokenToBackend = async (accessToken) => {
  try {
    // Django 서버로 요청 (포트번호 확인 필요: 보통 8000)
    const response = await axios.post('http://127.0.0.1:8000/users/kakao/login/', {
      access_token: accessToken,
    })

    console.log('로그인 성공:', response.data)
    
    // 토큰 저장 (Pinia나 localStorage 사용)
    localStorage.setItem('accessToken', response.data.key || response.data.access)
    
    alert('환영합니다!')
    router.push('/') // 메인 페이지로 이동

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