<template>
  <div class="detail-container" v-if="article">
    
    <div class="detail-header">
      <div class="header-top">
        <span class="category-badge">자유게시판</span>
        <div class="header-actions" v-if="isAuthor">
          <button @click="goToUpdate" class="action-btn edit">수정</button>
          <button @click="handleDelete" class="action-btn delete">삭제</button>
        </div>
      </div>

      <h1 class="article-title">{{ article.title }}</h1>
      
      <div class="article-meta">
        <div class="meta-left">
          <span class="author">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/></svg>
            {{ article.username }}
          </span>
          <span class="divider">|</span>
          <span class="date">{{ formatDate(article.created_at) }}</span>
        </div>
        <div class="meta-right">
          <span class="hits">조회 {{ article.hits }}</span>
        </div>
      </div>
    </div>

    <div v-if="article.image" class="article-image-wrapper">
      <img :src="`${API_URL}${article.image}`" alt="게시글 이미지">
    </div>

    <div class="article-body">
      <div class="content-text">{{ article.content }}</div>
    </div>

    <div v-if="article.course" class="course-summary-card">
      <div class="course-header">
        <span class="badge-region">{{ article.course.region }}</span>
        <h3 class="card-title">{{ article.course.title }}</h3>
      </div>
      
      <div class="course-body">
        <p class="course-date">
          📅 {{ article.course.start_date }} ~ {{ article.course.end_date }}
        </p>
        
        <div class="preview-itinerary">
          <div v-for="(spots, day) in groupedDetails" :key="day" class="day-row">
            <div class="day-label">Day {{ day }}</div>
            
            <div class="day-spots">
              <span v-for="(detail, idx) in spots" :key="detail.id" class="spot-item">
                {{ detail.trip_name || (detail.trip ? detail.trip.title : '여행지') }}
                
                <span v-if="idx < spots.length - 1" class="arrow">→</span>
              </span>
            </div>
          </div>
        </div>
      </div>
      </div>
    <div class="like-section">
      <button class="like-btn" @click="handleLike">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="heart-icon" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
        </svg>
        <span>좋아요 {{ article.like_count }}</span>
      </button>
    </div>
    
    <hr class="divider-line">
    
    <div class="comment-section">
      <h3>댓글 <span class="comment-count">{{ article.comment_set.length }}</span></h3>

      <div class="comment-form" v-if="accountStore.isLogin">
        <textarea 
          v-model="commentContent" 
          placeholder="따뜻한 댓글을 남겨주세요."
          @keyup.ctrl.enter="submitComment"
        ></textarea>
        <button @click="submitComment" class="submit-btn">등록</button>
      </div>
      
      <div v-else class="login-plz">
        댓글을 작성하려면 로그인이 필요합니다.
      </div>

      <div class="comment-list">
        <div v-for="comment in article.comment_set" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <div class="info-left">
              <span class="comment-author">{{ comment.username }}</span>
              <span class="comment-date">{{ formatTime(comment.created_at) }}</span>
            </div>
            
            <button 
              v-if="accountStore.user && accountStore.user.username === comment.username"
              @click="deleteComment(comment.id)"
              class="comment-delete-btn"
            >
              ✕
            </button>
          </div>
          <p class="comment-content">{{ comment.content }}</p>
        </div>
        
        <div v-if="article.comment_set.length === 0" class="no-comments">
          첫 번째 댓글의 주인공이 되어보세요!
        </div>
      </div>
    </div>

    <div class="bottom-nav">
      <button @click="goBack" class="list-btn">목록으로</button>
    </div>

  </div>
  
  <div v-else class="loading">
    게시글을 불러오는 중입니다...
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { useAccountStore } from '@/stores/accounts';
import { storeToRefs } from 'pinia';

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();
const accountStore = useAccountStore();
const { article } = storeToRefs(communityStore);

const commentContent = ref('');
const articleId = route.params.id;

const API_URL = 'http://127.0.0.1:8000';

const isAuthor = computed(() => {
  return accountStore.user && article.value && accountStore.user.username === article.value.username;
});

const groupedDetails = computed(() => {
  if (!article.value || !article.value.course || !article.value.course.details) {
    return {};
  }

  const groups = {};
  article.value.course.details.forEach(detail => {
    const day = detail.day;
    if (!groups[day]) {
      groups[day] = [];
    }
    groups[day].push(detail);
  });
  
  return Object.keys(groups).sort().reduce((acc, key) => {
    acc[key] = groups[key];
    return acc;
  }, {});
});

onMounted(() => {
  if (accountStore.token && !accountStore.user) {
    accountStore.getUserInfo();
  }
  communityStore.getArticleDetail(articleId);
});

// 게시글 삭제
const handleDelete = () => {
  communityStore.deleteArticle(articleId);
};

const deleteComment = (commentId) => {
  communityStore.deleteComment(articleId, commentId);
};


// 좋아요 클릭
const handleLike = () => {
  communityStore.likeArticle(articleId);
};

// 댓글 작성
const submitComment = async () => {
  if (!commentContent.value.trim()) {
    alert('내용을 입력해주세요.');
    return;
  }
  await communityStore.createComment(articleId, commentContent.value);
  commentContent.value = ''; // 입력창 초기화
};

// 목록으로
const goBack = () => {
  router.push({ name: 'community' });
};

// 날짜 포맷 (YYYY.MM.DD)
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR');
};

const goToUpdate = () => {
  router.push({ name: 'article-update', params: {
    id: articleId
  }})
}

// 시간 포맷 (방금 전, 또는 YYYY.MM.DD HH:mm)
const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', { 
    month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' 
  });
};

</script>

<style scoped>
  .article-image-wrapper {
  margin-top: 20px;
  text-align: center;
}
.article-image-wrapper img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  object-fit: contain;
}

.course-header {
  display: flex;
  gap: 15px;
  align-items: baseline;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.course-title { font-weight: 700; font-size: 18px; color: #7B9DFF; }
.course-region { font-weight: 600; color: #555; }
.course-period { font-size: 14px; color: #888; }

.course-timeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.timeline-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  border: 1px solid #eee;
}
.day-badge {
  background-color: #7B9DFF;
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
}
.place-name {
  font-weight: 500;
  color: #333;
}

.detail-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더 영역 */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-badge {
  background-color: #e3f2fd;
  color: #1e88e5;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.action-btn {
  background: none;
  border: none;
  font-size: 13px;
  cursor: pointer;
  margin-left: 10px;
  padding: 5px 10px;
  border-radius: 4px;
}

.action-btn.edit { color: #666; background-color: #f5f5f5; }
.action-btn.delete { color: #fff; background-color: #ff6b6b; }

.article-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.4;
  word-break: break-all; 
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #888;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.meta-left { display: flex; align-items: center; gap: 10px; }
.author { display: flex; align-items: center; gap: 6px; font-weight: 500; color: #555; }
.divider { color: #ddd; }

/* 본문 영역 */
.article-body {
  padding: 40px 0;
  min-height: 200px;
}

.content-text {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 좋아요 버튼 */
.like-section {
  text-align: center;
  margin-bottom: 30px;
}

.like-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border: 1px solid #ddd;
  border-radius: 30px;
  background-color: white;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  color: #555;
}

.like-btn:hover {
  border-color: #ff6b6b;
  color: #ff6b6b;
  background-color: #fff5f5;
}

.heart-icon {
  color: #ff6b6b;
}

.divider-line {
  border: none;
  border-top: 1px solid #eee;
  margin: 20px 0;
}

/* 댓글 영역 */
.comment-section {
  margin-top: 30px;
}

.comment-count {
  color: #7B9DFF;
}

.comment-form {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.comment-form textarea {
  width: 100%;
  height: 80px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  resize: none;
  outline: none;
  font-family: inherit;
}

.comment-form textarea:focus {
  border-color: #7B9DFF;
}

.submit-btn {
  padding: 8px 20px;
  background-color: #7B9DFF;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}

.login-plz {
  background-color: #f9f9f9;
  padding: 30px;
  text-align: center;
  color: #888;
  border-radius: 8px;
  font-size: 14px;
}

.comment-list {
  margin-top: 30px;
}

.comment-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  color: #555;
  line-height: 1.5;
  white-space: pre-wrap;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}

.comment-delete-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  padding: 0 5px;
  transition: color 0.2s;
}
.comment-delete-btn:hover {
  color: #ff6b6b;
}

.bottom-nav {
  margin-top: 40px;
  text-align: center;
}

.list-btn {
  padding: 10px 30px;
  background-color: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 100px;
  font-size: 18px;
  color: #888;
}

@media (max-width: 768px) {
  .detail-container {
    padding: 20px;
    margin: 20px;
  }
  
  .article-title {
    font-size: 22px;
  }
}

.course-summary-card {
  margin: 30px 0;
  padding: 25px;
  border: 1px solid #e0e7ff;
  border-left: 5px solid #7B9DFF;
  border-radius: 8px;
  background-color: #f8faff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.course-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.badge-region {
  background-color: #7B9DFF;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.course-date {
  color: #666;
  font-size: 15px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-spots {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
}

.spot-label {
  font-size: 13px;
  color: #888;
  font-weight: 600;
}

.spot-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  font-size: 15px;
  color: #495057;
}

.preview-itinerary {
  margin-top: 15px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e1f5fe;
}

.day-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}

.day-row:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.day-label {
  background-color: #7B9DFF;
  color: white;
  font-weight: 700;
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 15px;
  margin-right: 15px;
  flex-shrink: 0;
  min-width: 60px;
  text-align: center;
}

.day-spots {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.spot-item {
  display: inline-flex;
  align-items: center;
  font-weight: 600; 
  color: #333;
}

.arrow {
  color: #bbb;
  margin: 0 6px;
  font-size: 12px;
}
</style>