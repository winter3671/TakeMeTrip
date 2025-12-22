<template>
  <div class="signup-wrapper">
    <div class="signup-container">
      <h2 class="signup-title">회원가입</h2>

      <form class="signup-form" @submit.prevent="handleSignup">
        
        <div class="input-group">
          <label for="username">아이디</label>
          <input type="text" id="username" v-model.trim="username" placeholder="아이디를 입력하세요">
        </div>

        <div class="input-group">
          <label for="email">이메일</label>
          <input type="email" id="email" v-model.trim="email" placeholder="example@email.com">
        </div>

        <div class="input-group">
          <label for="password">비밀번호</label>
          <input type="password" id="password" v-model.trim="password" placeholder="비밀번호">
        </div>

        <div class="input-group">
          <label for="passwordConfirm">비밀번호 재입력</label>
          <input type="password" id="passwordConfirm" v-model.trim="passwordConfirm" placeholder="비밀번호 확인">
        </div>

        <button type="submit" class="signup-btn">회원가입</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAccountStore } from '@/stores/accounts';

const store = useAccountStore()

const username = ref('');
const email = ref('');
const password = ref('');
const passwordConfirm = ref('');

const handleSignup = () => {
  if (!username.value || !password.value || !passwordConfirm.value) {
    alert('모든 항목을 입력해주세요.');
    return;
  }

  if (password.value !== passwordConfirm.value) {
    alert('비밀번호가 일치하지 않습니다.');
    return;
  }

  const payload = {
    username: username.value,
    email: email.value,
    password1: password.value,
    password2: passwordConfirm.value
  };

  store.signUp(payload)

  console.log('Signup attempt:', {
    username: username.value,
    email: email.value,
    password: password.value
  });
};
</script>

<style scoped>
.signup-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #fff;
}

.signup-container {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  text-align: center;
}

.signup-title {
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
  font-size: 13px;
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

.signup-btn {
  width: 100%;
  padding: 15px 0;
  background-color: #1e6bba;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 20px;
  margin-bottom: 20px;
  transition: background-color 0.2s;
  box-shadow: 0 4px 6px rgba(30, 107, 186, 0.2);
}

.signup-btn:hover {
  background-color: #16528e;
}

</style>