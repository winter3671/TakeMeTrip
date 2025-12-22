<template>
  <div class="community-container">
    <div class="community-header">
      <h1 class="page-title">여행 커뮤니티</h1>
      <p class="page-subtitle">여행의 즐거움을 함께 나누고 정보를 공유해보세요.</p>
    </div>

    <div class="search-filter-bar">
      <div class="search-group">
        <select v-model="searchCondition" class="search-select">
          <option value="title_content">제목+내용</option>
          <option value="title">제목</option>
          <option value="content">내용</option>
          <option value="author">작성자</option>
        </select>
        <input 
          type="text" 
          v-model="searchKeyword" 
          @keyup.enter="handleSearch"
          placeholder="검색어를 입력하세요" 
          class="search-input"
        >
        <button @click="handleSearch" class="search-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
          </svg>
        </button>
      </div>
      
      <button v-if="accountStore.isLogin" @click="goToCreate" class="create-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
          <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
        </svg>
        글쓰기
      </button>
    </div>

    <div class="article-list">
      <div v-if="articles.length === 0" class="no-data">
        등록된 게시글이 없습니다. 첫 번째 글을 작성해보세요!
      </div>

      <div 
        v-else 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
        @click="goToDetail(article.id)"
      >
        <div class="article-content">
          <h3 class="article-title">{{ article.title }}</h3>
          <p class="article-preview">{{ article.content }}</p>
          
          <div class="article-meta">
            <span class="author">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/></svg>
              {{ article.username }}
            </span>
            <span class="date">{{ formatDate(article.created_at) }}</span>
          </div>
        </div>

        <div class="article-stats">
          <div class="stat-item" title="조회수">
            <span class="stat-label">조회</span>
            <span class="stat-value">{{ article.hits }}</span>
          </div>
          <div class="stat-item" title="좋아요">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="#FF6B6B" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/></svg>
            <span class="stat-value">{{ article.like_count }}</span>
          </div>
          <div class="stat-item" title="댓글">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="#4dabf7" viewBox="0 0 16 16"><path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/></svg>
            <span class="stat-value">{{ article.comment_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { useAccountStore } from '@/stores/accounts';
import { storeToRefs } from 'pinia';

const router = useRouter();
const communityStore = useCommunityStore();
const accountStore = useAccountStore();
const { articles } = storeToRefs(communityStore);

const searchKeyword = ref('');
const searchCondition = ref('title_content');

// 컴포넌트 마운트 시 게시글 목록 로드
onMounted(() => {
  communityStore.getArticles();
});

// 검색 핸들러
const handleSearch = () => {
  const params = {
    search: searchKeyword.value,
    condition: searchCondition.value
  };
  communityStore.getArticles(params);
};

// 게시글 상세 페이지 이동
const goToDetail = (id) => {
  router.push({ name: 'article-detail', params: { id } });
};

// 글쓰기 페이지 이동
const goToCreate = () => {
  router.push({ name: 'article-create' });
};

// 날짜 포맷팅 함수 (YYYY-MM-DD)
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};
</script>

<style scoped>
.community-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

.community-header {
  text-align: center;
  margin-bottom: 50px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.page-subtitle {
  color: #666;
  font-size: 16px;
}

/* 검색 및 필터 */
.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-group {
  display: flex;
  gap: 10px;
  flex: 1;
  max-width: 600px;
}

.search-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  cursor: pointer;
  background-color: #fff;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #7B9DFF;
}

.search-btn {
  padding: 0 15px;
  background-color: #7B9DFF;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.search-btn:hover {
  background-color: #5c85ff;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background-color: #000;
}

/* 게시글 리스트 */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.no-data {
  text-align: center;
  padding: 60px 0;
  color: #888;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.article-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  border-color: #7B9DFF;
}

.article-content {
  flex: 1;
  min-width: 0; /* flex 자식 내 말줄임 처리를 위해 필수 */
  margin-right: 20px;
}

.article-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-preview {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90%;
}

.article-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #888;
}

.author {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #555;
  font-weight: 500;
}

.article-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  min-width: 80px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.stat-value {
  font-weight: 600;
  color: #333;
}

@media (max-width: 768px) {
  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .create-btn {
    width: 100%;
    justify-content: center;
  }

  .article-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 20px;
  }

  .article-stats {
    flex-direction: row;
    width: 100%;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
    justify-content: flex-start;
    gap: 20px;
  }
}
</style>