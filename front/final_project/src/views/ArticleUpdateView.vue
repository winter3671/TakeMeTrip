<template>
  <div class="update-container">
    <h1 class="title">게시글 수정</h1>
    
    <div class="form-wrapper">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="articleData.title" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="articleData.content" 
          class="form-textarea"
        ></textarea>
      </div>

      <div class="btn-group">
        <button @click="updateArticle" class="submit-btn">수정 완료</button>
        <button @click="goBack" class="cancel-btn">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { storeToRefs } from 'pinia';

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();
const { article } = storeToRefs(communityStore);

const articleId = route.params.id;

// 수정할 데이터를 담을 변수
const articleData = ref({
  title: '',
  content: '',
});

onMounted(async () => {
  // 스토어에 데이터가 없으면 새로 불러옴
  if (!article.value || article.value.id != articleId) {
    await communityStore.getArticleDetail(articleId);
  }
  
  // 기존 데이터를 input창에 채워넣기
  articleData.value.title = article.value.title;
  articleData.value.content = article.value.content;
});

const updateArticle = () => {
  if(!articleData.value.title.trim() || !articleData.value.content.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  // Store의 수정 액션 호출
  communityStore.updateArticle(articleId, {
    title: articleData.value.title,
    content: articleData.value.content
  });
};

const goBack = () => {
  router.back();
};
</script>

<style scoped>
.update-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}

.form-wrapper {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-textarea {
  height: 300px;
  resize: none;
}

.form-input:focus, .form-textarea:focus {
  border-color: #7B9DFF;
}

.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.submit-btn {
  background-color: #7B9DFF;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn {
  background-color: #f1f3f5;
  color: #333;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.submit-btn:hover { background-color: #6388e5; }
.cancel-btn:hover { background-color: #e9ecef; }
</style>