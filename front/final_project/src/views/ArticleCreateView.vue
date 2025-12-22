<template>
  <div class="create-container">
    <h1 class="page-title">새 글 작성</h1>
    
    <form @submit.prevent="submitArticle" class="create-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="title" 
          placeholder="제목을 입력해주세요"
          required
        >
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="content" 
          placeholder="내용을 자유롭게 작성해주세요"
          required
        ></textarea>
      </div>

      <div class="btn-group">
        <button type="button" class="cancel-btn" @click="goBack">취소</button>
        <button type="submit" class="submit-btn">등록하기</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';

const communityStore = useCommunityStore();
const router = useRouter();

const title = ref('');
const content = ref('');

const submitArticle = () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  const payload = {
    title: title.value,
    content: content.value
  };

  communityStore.createArticle(payload);
};

const goBack = () => {
  router.back();
};
</script>

<style scoped>
.create-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  font-family: 'Noto Sans KR', sans-serif;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group textarea {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #7B9DFF;
}

.form-group textarea {
  height: 300px;
  resize: none;
  line-height: 1.6;
}

.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 10px;
}

.cancel-btn {
  padding: 12px 30px;
  background-color: #f1f3f5;
  color: #495057;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background-color: #e9ecef;
}

.submit-btn {
  padding: 12px 30px;
  background-color: #7B9DFF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover {
  background-color: #5c85ff;
}

@media (max-width: 768px) {
  .create-container {
    margin: 20px;
    padding: 20px;
  }
}
</style>