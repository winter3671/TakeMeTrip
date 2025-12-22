<template>
  <div class="callback-container">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p>로그인 처리 중입니다...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useAccountStore } from '@/stores/accounts';

const route = useRoute();
const router = useRouter();
const accountStore = useAccountStore();

onMounted(async () => {
  const { code, state } = route.query;

  // 네이버는 state 값이 필수적
  const provider = state ? 'naver' : 'google';

  if (code) {
    try {
      // 백엔드로 인가 코드 전송
      const response = await axios.post(`http://127.0.0.1:8000/api/auth/social/${provider}/login/`, {
        code: code,
        state: state
      });
      // 백엔드에서 받은 JWT 토큰 저장
      const accessToken = response.data.key || response.data.access;
      localStorage.setItem('accessToken', accessToken);
      
      // Pinia 스토어 업데이트
      accountStore.token = accessToken;
      
      console.log(`${provider} 로그인 성공!`);
      router.replace('/'); // 메인 페이지로 이동

    } catch (error) {
      console.error('소셜 로그인 실패:', error);
      alert('로그인에 실패했습니다. 다시 시도해주세요.');
      router.replace('/login');
    }
  } else {
    alert('잘못된 접근입니다.');
    router.replace('/login');
  }
});
</script>

<style scoped>
.callback-container {
  height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
</style>